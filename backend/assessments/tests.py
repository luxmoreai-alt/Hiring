from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
from unittest.mock import patch

from .auth import make_token
from .emails import send_completion_email, send_registration_email
from .models import (AssessmentReset, Attempt, Candidate, CandidateStatusHistory,
                     ProctorEvent, ProctorRecording, ProctorRecordingChunk,
                     Question, Response)
from .runner import _judge0_languages_cache, available_languages, run_code
from .views import advance, evaluate_react_solution, public_question


class AssessmentFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_questions", verbosity=0)
        cls.admin = get_user_model().objects.create_user(username="recruiter", password="test-password", is_staff=True)

    def setUp(self):
        self.client = APIClient()

    def register_candidate(self):
        response = self.client.post("/api/candidates/register/", {
            "name": "Test Student", "email": "student@example.com", "phone": "9876543210",
            "college": "Example Institute", "designation": "B.Tech CSE",
            "address": "12 Example Road, Hyderabad 500001", "address_confirmed": "true",
            "role": "mern-stack-developer", "preferred_location": "hyderabad",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['token']}")
        return response.data

    def test_question_bank_has_required_counts(self):
        self.assertGreater(Question.objects.filter(round_type="aptitude").count(), 60)
        self.assertGreater(Question.objects.filter(round_type="technical", role="mern-stack-developer").count(), 20)
        self.assertGreater(Question.objects.filter(round_type="coding", role="mern-stack-developer").count(), 2)
        for role in ("frontend-developer", "backend-developer", "full-stack-developer"):
            self.assertGreater(Question.objects.filter(round_type="technical", role=role).count(), 20)
            self.assertGreater(Question.objects.filter(round_type="coding", role=role).count(), 2)
        frontend = Question.objects.filter(round_type="coding", role="frontend-developer").first()
        self.assertEqual(public_question(frontend)["workspace"], "react")
        self.assertEqual(public_question(frontend)["languages"], [{"value": "react", "label": "React (JSX)"}])

    def test_react_challenge_evaluator_reports_requirements(self):
        results = evaluate_react_solution(
            "function App(){ return <nav><a href='#work'>Work</a></nav>; }",
            [{"label": "Navigation", "all": ["<nav", "href="]}],
        )
        self.assertTrue(results[0]["passed"])

    def test_register_start_and_answer(self):
        self.register_candidate()
        started = self.client.post("/api/rounds/aptitude/start/", {}, format="json")
        self.assertEqual(started.status_code, 201)
        self.assertEqual(started.data["total"], 60)
        self.assertNotIn("correct_option", started.data["question"])
        question = Question.objects.get(id=started.data["question"]["id"])
        answered = self.client.post("/api/rounds/aptitude/answer/", {
            "question_id": question.id, "selected_option": question.correct_option,
        }, format="json")
        self.assertEqual(answered.status_code, 200)
        self.assertNotIn("score", answered.data["state"])
        self.assertEqual(answered.data["state"]["current"], 1)

    def test_registration_stores_college_name_in_capital_letters(self):
        registration = self.register_candidate()
        candidate = Candidate.objects.get(id=registration["candidate"]["id"])
        self.assertEqual(candidate.college, "EXAMPLE INSTITUTE")
        self.assertEqual(registration["candidate"]["college"], "EXAMPLE INSTITUTE")

    def test_duplicate_answer_returns_current_state_without_error(self):
        registration = self.register_candidate()
        started = self.client.post("/api/rounds/aptitude/start/", {}, format="json")
        question = Question.objects.get(id=started.data["question"]["id"])
        payload = {"question_id": question.id, "selected_option": question.correct_option}
        first = self.client.post("/api/rounds/aptitude/answer/", payload, format="json")
        duplicate = self.client.post("/api/rounds/aptitude/answer/", payload, format="json")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(duplicate.status_code, 200)
        self.assertTrue(duplicate.data["duplicate"])
        self.assertEqual(duplicate.data["state"]["current"], 1)
        candidate = Candidate.objects.get(id=registration["candidate"]["id"])
        self.assertEqual(candidate.attempts.get(round_type="aptitude").responses.count(), 1)

    def test_every_completed_round_advances_without_a_score_threshold(self):
        cases = [
            ("aptitude", "aptitude", "technical", "assessment_pending"),
            ("technical", "technical", "coding", "assessment_pending"),
            ("coding", "coding", "completed", "assessment_completed"),
        ]
        for index, (round_type, starting_status, expected_status, expected_hiring) in enumerate(cases):
            with self.subTest(round_type=round_type):
                candidate = Candidate.objects.create(
                    name=f"Completed {round_type}", email=f"completed-{index}@example.com",
                    phone=f"97654321{index:02d}", college="Example Institute",
                    designation="B.Tech", address="Chennai", role="mern-stack-developer",
                    status=starting_status,
                )
                attempt = Attempt.objects.create(
                    candidate=candidate, round_type=round_type, question_ids=[1],
                    score=Decimal("0"), max_score=Decimal("20"),
                )

                advance(attempt)
                candidate.refresh_from_db()

                self.assertEqual(candidate.status, expected_status)
                self.assertEqual(candidate.hiring_status, expected_hiring)
                self.assertFalse(CandidateStatusHistory.objects.filter(
                    candidate=candidate, to_status="rejected",
                ).exists())

    def test_stale_coding_requests_return_conflict_instead_of_not_found(self):
        self.register_candidate()
        state = self.client.get("/api/rounds/coding/state/")
        run = self.client.post("/api/rounds/coding/run/", {
            "code": "print('test')", "language": "python",
        }, format="json")
        answer = self.client.post("/api/rounds/coding/answer/", {
            "question_id": 1, "code": "print('test')", "language": "python",
        }, format="json")
        self.assertEqual(state.status_code, 409)
        self.assertEqual(run.status_code, 409)
        self.assertEqual(answer.status_code, 409)

    def test_matching_email_and_phone_resumes_registration(self):
        first = self.register_candidate()
        self.client.credentials()
        response = self.client.post("/api/candidates/register/", {
            "name": "Test Student", "email": "student@example.com", "phone": "9876543210",
            "college": "Example Institute", "designation": "B.Tech CSE",
            "address": "12 Example Road, Hyderabad 500001", "address_confirmed": True,
            "role": "mern-stack-developer", "preferred_location": "hyderabad",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["resumed"])
        self.assertEqual(response.data["candidate"]["id"], first["candidate"]["id"])

    def test_college_names_are_normalized_for_filtering(self):
        first = Candidate.objects.create(name="A", email="college-a@example.com", phone="9999999999", college="Example   INSTITUTE", designation="B", address="X", role="data-analyst")
        second = Candidate.objects.create(name="B", email="college-b@example.com", phone="8888888888", college=" example institute ", designation="B", address="X", role="data-analyst")
        self.assertEqual(first.college_normalized, second.college_normalized)

    @patch.dict("assessments.views.os.environ", {"TEST_RETAKE_EMAILS": "luxmoreai@gmail.com"}, clear=False)
    def test_reserved_test_email_can_restart_an_assessment(self):
        candidate = Candidate.objects.create(
            name="Luxmore Test", email="luxmoreai@gmail.com", phone="9876543210",
            college="Luxmore", designation="Tester", address="Chennai",
            role="mern-stack-developer", status="completed", hiring_status="assessment_completed",
        )
        attempt = candidate.attempts.create(round_type="aptitude", question_ids=[1], status="completed")
        response = self.client.post("/api/candidates/register/", {
            "name": "Luxmore Test", "email": candidate.email, "phone": "9884050511",
            "college": candidate.college, "designation": candidate.designation,
            "address": "12 Test Road, Chennai 600001", "address_confirmed": True,
            "role": candidate.role, "preferred_location": "chennai",
        }, format="json")
        candidate.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["restarted"])
        self.assertEqual(candidate.status, "registered")
        self.assertEqual(candidate.phone, "9884050511")
        self.assertFalse(Candidate.objects.get(id=candidate.id).attempts.exists())

    @override_settings(
        EMAIL_NOTIFICATIONS_ENABLED=True,
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="careers@luxmorai.com",
    )
    def test_branded_registration_and_completion_emails(self):
        candidate = Candidate.objects.create(
            name="Mail Candidate",
            email="mail-candidate@example.com",
            phone="9876543210",
            college="Example Institute",
            designation="B.Tech CSE",
            address="Chennai",
            role="frontend-developer",
            preferred_location="chennai",
        )
        self.assertTrue(send_registration_email(candidate))
        self.assertTrue(send_completion_email(candidate))
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [candidate.email])
        self.assertIn("Registration confirmed", mail.outbox[0].subject)
        self.assertIn("Assessment submitted", mail.outbox[1].subject)
        self.assertEqual(mail.outbox[0].alternatives[0].mimetype, "text/html")
        self.assertIn("Luxmor TalentForge", mail.outbox[0].alternatives[0].content)
        inline_logo = [
            attachment
            for attachment in mail.outbox[0].attachments
            if attachment.get("Content-ID") == "<luxmor-logo>"
        ]
        self.assertEqual(len(inline_logo), 1)

    def test_code_runner_reports_passes(self):
        results = run_code("a,b=map(int,input().split());print(a+b)", "python", [
            {"input": "2 3\n", "output": "5"}, {"input": "8 7\n", "output": "15"},
        ])
        self.assertTrue(all(item["passed"] for item in results))

    def test_all_advertised_languages_execute(self):
        cases = [{"input": "2 3\n", "output": "5"}]
        solutions = {
            "python": "a,b=map(int,input().split());print(a+b)",
            "javascript": "const [a,b]=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);console.log(a+b)",
            "typescript": "import * as fs from 'fs'; const v:number[]=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number); console.log(v[0]+v[1]);",
            "java": "import java.util.*; public class Main { public static void main(String[] a){ Scanner s=new Scanner(System.in); System.out.println(s.nextInt()+s.nextInt()); }}",
        }
        for language in [item["value"] for item in available_languages()]:
            with self.subTest(language=language):
                self.assertTrue(run_code(solutions[language], language, cases)[0]["passed"])

    @override_settings()
    @patch.dict("os.environ", {"JUDGE0_API_URL": "https://judge.example.com"}, clear=False)
    @patch("assessments.runner._judge0_request")
    def test_judge0_catalogue_is_used_when_configured(self, request):
        _judge0_languages_cache.update(expires=0, languages=[])
        request.return_value = [{"id": 71, "name": "Python (3.8.1)"}, {"id": 63, "name": "JavaScript (Node.js 12.14.0)"}]
        self.assertEqual(available_languages(), [
            {"value": "judge0:71", "label": "Python (3.8.1)"},
            {"value": "judge0:63", "label": "JavaScript (Node.js 12.14.0)"},
        ])

    def test_staff_dashboard(self):
        candidate = Candidate.objects.create(name="A", email="a@example.com", phone="99999999", college="C", designation="B.Tech", address="X", role="data-analyst")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(self.admin.id, 'admin')}")
        response = self.client.get("/api/staff/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["summary"]["registered"], 1)
        self.assertEqual(response.data["candidates"][0]["id"], str(candidate.id))

    def test_staff_dashboard_handles_200_candidates_without_n_plus_one_queries(self):
        Candidate.objects.bulk_create([
            Candidate(name=f"Candidate {index}", email=f"candidate-{index}@example.com",
                      phone=f"9{index:09d}", college="Load Test College", designation="B.Tech",
                      address="Load Test Address", role="data-analyst")
            for index in range(200)
        ])
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(self.admin.id, 'admin')}")
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get("/api/staff/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["candidates"]), 200)
        self.assertLessEqual(len(queries), 5)

    def test_staff_can_update_recruitment_status(self):
        candidate = Candidate.objects.create(name="Interview Candidate", email="interview@example.com", phone="99999999", college="C", designation="B.Tech", address="X", role="data-analyst", preferred_location="chennai")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(self.admin.id, 'admin')}")
        response = self.client.patch(f"/api/staff/candidates/{candidate.id}/status/", {
            "hiring_status": "technical_completed", "note": "Technical panel cleared",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        candidate.refresh_from_db()
        self.assertEqual(candidate.hiring_status, "technical_completed")
        self.assertTrue(CandidateStatusHistory.objects.filter(candidate=candidate, to_status="technical_completed").exists())

    def test_staff_can_delete_candidate(self):
        candidate = Candidate.objects.create(name="Delete Me", email="delete@example.com", phone="99999999", college="C", designation="B.Tech", address="X", role="data-analyst")
        question = Question.objects.first()
        attempt = Attempt.objects.create(candidate=candidate, round_type="aptitude", question_ids=[question.id])
        Response.objects.create(attempt=attempt, question=question)
        ProctorEvent.objects.create(candidate=candidate, attempt=attempt, event_type="tab_hidden")
        CandidateStatusHistory.objects.create(candidate=candidate, to_status="on_hold")
        AssessmentReset.objects.create(candidate=candidate, assessment_cycle=1, status_before_reset="aptitude")
        recording = ProctorRecording.objects.create(candidate=candidate, attempt=attempt, kind="screen")
        ProctorRecordingChunk.objects.create(recording=recording, sequence=0, data=b"screen-video")
        related_ids = {"attempt": attempt.id, "recording": recording.id}
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(self.admin.id, 'admin')}")
        response = self.client.delete(f"/api/staff/candidates/{candidate.id}/delete/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["deleted"])
        self.assertFalse(Candidate.objects.filter(id=candidate.id).exists())
        self.assertFalse(Attempt.objects.filter(id=related_ids["attempt"]).exists())
        self.assertFalse(Response.objects.filter(attempt_id=related_ids["attempt"]).exists())
        self.assertFalse(ProctorEvent.objects.filter(candidate_id=candidate.id).exists())
        self.assertFalse(CandidateStatusHistory.objects.filter(candidate_id=candidate.id).exists())
        self.assertFalse(AssessmentReset.objects.filter(candidate_id=candidate.id).exists())
        self.assertFalse(ProctorRecording.objects.filter(id=related_ids["recording"]).exists())
        self.assertFalse(ProctorRecordingChunk.objects.filter(recording_id=related_ids["recording"]).exists())

    def test_staff_can_bulk_delete_only_selected_candidates(self):
        Candidate.objects.create(name="Selected", email="selected@example.com", phone="9999999999", college="C", designation="B", address="X", role="data-analyst", hiring_status="selected")
        kept = Candidate.objects.create(name="Pending", email="pending@example.com", phone="8888888888", college="C", designation="B", address="X", role="data-analyst")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(self.admin.id, 'admin')}")
        response = self.client.delete("/api/staff/selected/delete-all/")
        self.assertEqual(response.data["deleted"], 1)
        self.assertTrue(Candidate.objects.filter(id=kept.id).exists())

    def test_staff_can_bulk_delete_only_rejected_candidates(self):
        for index in range(3):
            Candidate.objects.create(name=f"Rejected {index}", email=f"rejected{index}@example.com", phone=f"999999999{index}", college="C", designation="B", address="X", role="data-analyst", hiring_status="rejected")
        kept = Candidate.objects.create(name="Selected", email="selected-kept@example.com", phone="8888888888", college="C", designation="B", address="X", role="data-analyst", hiring_status="selected")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(self.admin.id, 'admin')}")
        response = self.client.delete("/api/staff/rejected/delete-all/?limit=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["deleted"], 2)
        self.assertEqual(response.data["remaining"], 1)
        self.assertTrue(Candidate.objects.filter(id=kept.id).exists())

    def test_staff_reset_preserves_previous_attempt_and_allows_retake(self):
        registration = self.register_candidate()
        started = self.client.post("/api/rounds/aptitude/start/", {}, format="json")
        candidate = Candidate.objects.get(id=registration["candidate"]["id"])
        old_attempt_id = started.data["id"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(self.admin.id, 'admin')}")
        reset = self.client.post(f"/api/staff/candidates/{candidate.id}/reset/", {}, format="json")
        self.assertEqual(reset.status_code, 200)
        candidate.refresh_from_db()
        self.assertEqual(candidate.status, "registered")
        self.assertEqual(candidate.assessment_cycle, 2)
        self.assertFalse(candidate.access_locked)
        self.assertTrue(candidate.attempts.filter(id=old_attempt_id, assessment_cycle=1).exists())
        self.assertTrue(AssessmentReset.objects.filter(candidate=candidate, assessment_cycle=1).exists())
        self.assertEqual(reset.data["candidate"]["previous_assessments"][0]["rounds"][0]["round_type"], "aptitude")

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(candidate.id)}")
        restarted = self.client.post("/api/rounds/aptitude/start/", {}, format="json")
        self.assertEqual(restarted.status_code, 201)
        self.assertNotEqual(restarted.data["id"], old_attempt_id)
