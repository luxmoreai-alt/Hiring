from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .auth import make_token
from .emails import send_completion_email, send_registration_email
from .models import Candidate, CandidateStatusHistory, Question
from .runner import available_languages, run_code
from .views import evaluate_react_solution, public_question


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
            "address": "Hyderabad", "role": "software-developer", "preferred_location": "hyderabad",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['token']}")
        return response.data

    def test_question_bank_has_required_counts(self):
        self.assertEqual(Question.objects.filter(round_type="aptitude").count(), 60)
        self.assertEqual(Question.objects.filter(round_type="technical", role="software-developer").count(), 20)
        self.assertEqual(Question.objects.filter(round_type="coding", role="software-developer").count(), 2)
        for role in ("frontend-developer", "backend-developer", "full-stack-developer"):
            self.assertEqual(Question.objects.filter(round_type="technical", role=role).count(), 20)
            self.assertEqual(Question.objects.filter(round_type="coding", role=role).count(), 2)
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
        self.assertEqual(answered.data["state"]["score"], 1)
        self.assertEqual(answered.data["state"]["current"], 1)

    def test_matching_email_and_phone_resumes_registration(self):
        first = self.register_candidate()
        self.client.credentials()
        response = self.client.post("/api/candidates/register/", {
            "name": "Test Student", "email": "student@example.com", "phone": "9876543210",
            "college": "Example Institute", "designation": "B.Tech CSE",
            "address": "Hyderabad", "role": "software-developer", "preferred_location": "hyderabad",
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["resumed"])
        self.assertEqual(response.data["candidate"]["id"], first["candidate"]["id"])

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

    def test_staff_dashboard(self):
        candidate = Candidate.objects.create(name="A", email="a@example.com", phone="99999999", college="C", designation="B.Tech", address="X", role="data-analyst")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(self.admin.id, 'admin')}")
        response = self.client.get("/api/staff/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["summary"]["registered"], 1)
        self.assertEqual(response.data["candidates"][0]["id"], str(candidate.id))

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
