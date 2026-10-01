import os
import random
import re
from decimal import Decimal
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response as ApiResponse
from rest_framework import status

from .auth import make_token, read_token
from .deletion import delete_candidates
from .emails import send_completion_email, send_registration_email
from .models import (AssessmentReset, Attempt, Candidate, CandidateStatusHistory,
                     Question, Response)
from .runner import DEFAULT_STARTERS, available_languages, run_code

ROUND_ORDER = ["aptitude", "technical", "coding"]
ROUND_LIMITS = {"aptitude": 60, "technical": 20, "coding": 2}
QUESTION_SECONDS = {"aptitude": 60, "technical": 60, "coding": 1200}


def normalized_college(value):
    return " ".join(str(value).split()).casefold()


def candidate_for(request):
    return get_object_or_404(Candidate, id=read_token(request))


QUESTION_CACHE = {}


def test_retake_emails():
    return {
        email.strip().lower()
        for email in os.environ.get("TEST_RETAKE_EMAILS", "luxmoreai@gmail.com").split(",")
        if email.strip()
    }


def cached_question(question_id):
    """Questions are immutable during a hiring drive; avoid a Neon read on every answer."""
    question_id = int(question_id)
    if question_id not in QUESTION_CACHE:
        QUESTION_CACHE[question_id] = Question.objects.get(id=question_id)
    return QUESTION_CACHE[question_id]


def warm_questions(question_ids):
    missing = [int(question_id) for question_id in question_ids if int(question_id) not in QUESTION_CACHE]
    if missing:
        QUESTION_CACHE.update(Question.objects.in_bulk(missing))


def candidate_data(candidate, detailed=False, include_results=False):
    data = {
        "id": str(candidate.id), "name": candidate.name, "email": candidate.email,
        "phone": candidate.phone, "college": candidate.college, "designation": candidate.designation,
        "gender": candidate.gender, "gender_label": candidate.get_gender_display(),
        "address": candidate.address, "role": candidate.role, "role_label": candidate.get_role_display(),
        "preferred_location": candidate.preferred_location, "preferred_location_label": candidate.get_preferred_location_display(),
        "status": candidate.status, "hiring_status": candidate.hiring_status,
        "hiring_status_label": candidate.get_hiring_status_display(), "registered_at": candidate.registered_at,
        "access_locked": False, "assessment_cycle": candidate.assessment_cycle,
        "ai_rejection_reason": candidate.ai_rejection_reason,
        "ai_rejected_at": candidate.ai_rejected_at,
    }
    prefetched_attempts = getattr(candidate, "_prefetched_objects_cache", {}).get("attempts")
    attempts = ([attempt for attempt in prefetched_attempts if attempt.assessment_cycle == candidate.assessment_cycle]
                if prefetched_attempts is not None
                else candidate.attempts.filter(assessment_cycle=candidate.assessment_cycle))
    data["rounds"] = [{
        "round_type": a.round_type, "status": a.status,
        **({
            "score": float(a.score), "max_score": float(a.max_score),
            "passed_tests": a.passed_tests, "total_tests": a.total_tests,
        } if include_results else {}),
    } for a in attempts]
    if detailed:
        data["responses"] = [{
            "round": r.attempt.round_type, "question": r.question.prompt,
            "category": r.question.category, "correct": r.is_correct,
            "score": float(r.score), "passed_tests": r.passed_tests,
            "total_tests": r.total_tests, "timed_out": r.timed_out,
        } for r in Response.objects.filter(attempt__candidate=candidate, attempt__assessment_cycle=candidate.assessment_cycle).select_related("attempt", "question")]
        data["previous_assessments"] = [{
            "assessment_cycle": reset.assessment_cycle, "status": reset.status_before_reset,
            "reset_at": reset.created_at,
            "reset_by": reset.reset_by.username if reset.reset_by else "System",
            "rounds": [{
                "round_type": attempt.round_type, "status": attempt.status,
                "score": float(attempt.score), "max_score": float(attempt.max_score),
                "passed_tests": attempt.passed_tests, "total_tests": attempt.total_tests,
            } for attempt in candidate.attempts.filter(assessment_cycle=reset.assessment_cycle)],
        } for reset in candidate.assessment_resets.select_related("reset_by").all()]
        data["status_history"] = [{
            "from_status": h.from_status, "to_status": h.to_status,
            "to_status_label": h.get_to_status_display(), "note": h.note,
            "changed_by": h.changed_by.username if h.changed_by else "System", "created_at": h.created_at,
        } for h in candidate.status_history.select_related("changed_by").all()]
    return data


def public_question(question):
    data = {"id": question.id, "prompt": question.prompt, "category": question.category, "round_type": question.round_type}
    if question.round_type == "coding":
        react_workspace = "react" in question.starter_code
        starters = question.starter_code if react_workspace else {**DEFAULT_STARTERS, **question.starter_code}
        languages = ([{"value": "react", "label": "React (JSX)"}]
                     if react_workspace else available_languages())
        data.update({
            "starter_code": starters,
            "visible_tests": question.test_cases[:question.visible_test_count],
            "languages": languages,
            "workspace": "react" if react_workspace else "console",
        })
    else:
        data["options"] = question.options
    return data


def evaluate_react_solution(code, test_cases):
    """Evaluate UI requirements without executing untrusted browser code on the API."""
    normalized = " ".join(code.lower().split())
    results = []
    for case in test_cases:
        required = [term.lower() for term in case.get("all", [])]
        alternatives = [term.lower() for term in case.get("any", [])]
        missing = [term for term in required if term not in normalized]
        alternative_found = not alternatives or any(term in normalized for term in alternatives)
        passed = not missing and alternative_found
        results.append({
            "passed": passed,
            "actual": "Requirement detected" if passed else "Implementation not detected",
            "expected": case.get("label", "UI requirement"),
            "label": case.get("label", "UI requirement"),
            "error": "" if passed else case.get("hint", "Complete this requirement and check again."),
        })
    return results


def attempt_state(attempt):
    total = len(attempt.question_ids)
    payload = {
        "id": attempt.id, "round_type": attempt.round_type, "status": attempt.status,
        "current": attempt.current_index, "total": total,
        "question_seconds": QUESTION_SECONDS[attempt.round_type],
    }
    if attempt.status == "in_progress" and attempt.current_index < total:
        question = cached_question(attempt.question_ids[attempt.current_index])
        elapsed = (timezone.now() - attempt.question_started_at).total_seconds() if attempt.question_started_at else 0
        payload["remaining_seconds"] = max(0, QUESTION_SECONDS[attempt.round_type] - int(elapsed))
        payload["question"] = public_question(question)
        if attempt.current_index + 1 < total:
            payload["next_question"] = public_question(cached_question(attempt.question_ids[attempt.current_index + 1]))
    return payload


def advance(attempt, auto=False):
    completed_assessment = False
    completed_candidate = None
    attempt.current_index += 1
    if attempt.current_index >= len(attempt.question_ids):
        attempt.status = "auto_submitted" if auto else "completed"
        attempt.completed_at = timezone.now()
        attempt.question_started_at = None
        candidate = attempt.candidate
        if attempt.round_type == "aptitude":
            candidate.status = "technical"
        elif attempt.round_type == "technical":
            candidate.status = "coding"
        else:
            candidate.status = "completed"
            candidate.completed_at = timezone.now()
            completed_assessment = True
            if candidate.hiring_status == "assessment_pending":
                candidate.hiring_status = "assessment_completed"
                candidate.hiring_status_updated_at = timezone.now()
        candidate.save(update_fields=[
            "status", "completed_at", "hiring_status", "hiring_status_updated_at",
            "ai_rejection_reason", "ai_rejected_at",
        ])
        if completed_assessment:
            completed_candidate = candidate
    else:
        attempt.question_started_at = timezone.now()
    attempt.save()
    if completed_candidate:
        send_completion_email(completed_candidate)


@api_view(["GET"])
def health(request):
    return ApiResponse({"status": "ok", "service": "Luxmor TalentForge API"})


@api_view(["POST"])
def register(request):
    required = ["name", "email", "phone", "college", "designation", "gender", "address", "role", "preferred_location"]
    missing = [field for field in required if not str(request.data.get(field, "")).strip()]
    if missing:
        return ApiResponse({"detail": f"Required fields: {', '.join(missing)}"}, status=400)
    email = request.data["email"].strip().lower()
    try:
        validate_email(email)
    except ValidationError:
        return ApiResponse({"detail": "Enter a valid email address."}, status=400)
    phone = re.sub(r"\s+", "", str(request.data["phone"]))
    if not re.fullmatch(r"[0-9]{10}", phone):
        return ApiResponse({"detail": "Phone number must contain exactly 10 digits."}, status=400)
    address = " ".join(str(request.data["address"]).split())
    if len(address) < 20 or not re.search(r"\b[1-9][0-9]{5}\b", address):
        return ApiResponse({"detail": "Enter the complete address shown on Aadhaar, including a valid 6-digit PIN code."}, status=400)
    if str(request.data.get("address_confirmed", "")).lower() not in ("true", "1", "yes"):
        return ApiResponse({"detail": "Confirm that the address matches the candidate's Aadhaar record."}, status=400)
    if request.data["role"] not in dict(Candidate.ROLE_CHOICES):
        return ApiResponse({"detail": "Please select a valid role"}, status=400)
    if request.data["preferred_location"] not in dict(Candidate.LOCATION_CHOICES):
        return ApiResponse({"detail": "Please select a valid preferred work location"}, status=400)
    if request.data["gender"] not in dict(Candidate.GENDER_CHOICES):
        return ApiResponse({"detail": "Please select a valid gender option"}, status=400)
    college = " ".join(str(request.data["college"]).split()).upper()
    college_key = normalized_college(college)
    canonical = Candidate.objects.filter(college_normalized=college_key).exclude(college="").values_list("college", flat=True).first()
    college = (canonical or college).upper()
    existing = Candidate.objects.filter(email=email).first()
    if existing:
        if email in test_retake_emails():
            # Reserved test account: refresh its details and erase prior attempts so it
            # can run a fresh full assessment, even if the test phone number changes.
            for field in required:
                setattr(existing, field, str(request.data[field]).strip())
            existing.phone, existing.address = phone, address
            existing.college, existing.college_normalized = college, college_key
            existing.attempts.all().delete()
            existing.proctor_events.all().delete()
            existing.status = "registered"
            existing.completed_at = None
            existing.hiring_status = "assessment_pending"
            existing.hiring_status_updated_at = timezone.now()
            existing.save(update_fields=[*required, "college_normalized", "status", "completed_at", "hiring_status", "hiring_status_updated_at"])
            return ApiResponse({"token": make_token(existing.id), "candidate": candidate_data(existing), "restarted": True})
        if existing.phone == phone:
            if existing.hiring_status == "rejected":
                with transaction.atomic():
                    existing = Candidate.objects.select_for_update().get(id=existing.id)
                    AssessmentReset.objects.create(
                        candidate=existing,
                        assessment_cycle=existing.assessment_cycle,
                        status_before_reset=existing.status,
                        reset_by=None,
                    )
                    for field in required:
                        if field != "email":
                            setattr(existing, field, str(request.data[field]).strip())
                    existing.phone, existing.address = phone, address
                    existing.college, existing.college_normalized = college, college_key
                    existing.assessment_cycle += 1
                    existing.status = "registered"
                    existing.access_locked = False
                    existing.completed_at = None
                    existing.hiring_status = "assessment_pending"
                    existing.hiring_status_updated_at = timezone.now()
                    existing.ai_rejection_reason = ""
                    existing.ai_rejected_at = None
                    existing.save(update_fields=[
                        "name", "phone", "college", "college_normalized", "designation", "gender",
                        "address", "role", "preferred_location", "assessment_cycle",
                        "status", "access_locked", "completed_at", "hiring_status",
                        "hiring_status_updated_at", "ai_rejection_reason", "ai_rejected_at",
                    ])
                return ApiResponse({
                    "token": make_token(existing.id),
                    "candidate": candidate_data(existing),
                    "restarted": True,
                })
            return ApiResponse({"token": make_token(existing.id), "candidate": candidate_data(existing), "resumed": True})
        return ApiResponse({"detail": "This email is already registered with a different phone number. Contact the recruiter for help."}, status=409)
    values = {field: str(request.data[field]).strip() for field in required if field != "email"}
    values.update(phone=phone, address=address, college=college, college_normalized=college_key)
    candidate = Candidate.objects.create(**values, email=email)
    send_registration_email(candidate)
    return ApiResponse({"token": make_token(candidate.id), "candidate": candidate_data(candidate)}, status=201)


@api_view(["GET"])
def me(request):
    return ApiResponse(candidate_data(candidate_for(request)))


@api_view(["POST"])
def start_round(request, round_type):
    candidate = candidate_for(request)
    if candidate.hiring_status == "rejected":
        return ApiResponse({"detail": candidate.ai_rejection_reason or "This assessment has ended."}, status=423)
    if round_type not in ROUND_ORDER:
        return ApiResponse({"detail": "Unknown round"}, status=404)
    expected = "aptitude" if candidate.status == "registered" else candidate.status
    existing = Attempt.objects.filter(candidate=candidate, round_type=round_type, assessment_cycle=candidate.assessment_cycle).first()
    if existing:
        warm_questions(existing.question_ids)
        return ApiResponse(attempt_state(existing))
    if expected != round_type:
        return ApiResponse({"detail": f"Complete the {expected} stage first"}, status=409)
    query = Question.objects.filter(active=True, round_type=round_type)
    if round_type in ("technical", "coding"):
        query = query.filter(role=candidate.role)
    ids = list(query.values_list("id", flat=True))
    needed = ROUND_LIMITS[round_type]
    if len(ids) < needed:
        return ApiResponse({"detail": f"Question bank is not ready: {len(ids)}/{needed} {round_type} questions available"}, status=503)
    random.shuffle(ids)
    warm_questions(ids[:needed])
    attempt = Attempt.objects.create(candidate=candidate, round_type=round_type, assessment_cycle=candidate.assessment_cycle, question_ids=ids[:needed], question_started_at=timezone.now(), max_score=needed * (10 if round_type == "coding" else 1))
    candidate.status = round_type
    candidate.save(update_fields=["status"])
    return ApiResponse(attempt_state(attempt), status=201)


@api_view(["GET"])
def round_state(request, round_type):
    candidate = candidate_for(request)
    if candidate.hiring_status == "rejected":
        return ApiResponse({"detail": candidate.ai_rejection_reason or "This assessment has ended."}, status=423)
    attempt = Attempt.objects.filter(
        candidate=candidate,
        round_type=round_type,
        assessment_cycle=candidate.assessment_cycle,
    ).first()
    if not attempt:
        return ApiResponse({"detail": "This assessment attempt is no longer available. Return to the assessment centre."}, status=409)
    warm_questions(attempt.question_ids)
    return ApiResponse(attempt_state(attempt))


@api_view(["POST"])
@transaction.atomic
def submit_answer(request, round_type):
    candidate = candidate_for(request)
    if candidate.hiring_status == "rejected":
        return ApiResponse({"detail": candidate.ai_rejection_reason or "This assessment has ended."}, status=423)
    attempt = Attempt.objects.select_for_update().filter(
        candidate=candidate,
        round_type=round_type,
        assessment_cycle=candidate.assessment_cycle,
    ).first()
    if not attempt:
        return ApiResponse({"detail": "This assessment attempt is no longer available. Return to the assessment centre."}, status=409)
    submitted_question_id = request.data.get("question_id")
    if attempt.status != "in_progress":
        if Response.objects.filter(attempt=attempt, question_id=submitted_question_id).exists():
            return ApiResponse({
                "accepted": True,
                "duplicate": True,
                "timed_out": False,
                "state": attempt_state(attempt),
            })
        return ApiResponse({"detail": "This assessment round is already complete."}, status=409)
    question = cached_question(attempt.question_ids[attempt.current_index])
    if str(submitted_question_id) != str(question.id):
        if Response.objects.filter(attempt=attempt, question_id=submitted_question_id).exists():
            return ApiResponse({
                "accepted": True,
                "duplicate": True,
                "timed_out": False,
                "state": attempt_state(attempt),
            })
        return ApiResponse({"detail": "Question has already advanced. Refresh the assessment."}, status=409)
    elapsed = (timezone.now() - attempt.question_started_at).total_seconds()
    timed_out = elapsed > QUESTION_SECONDS[round_type] + 3
    response = Response(attempt=attempt, question=question, timed_out=timed_out)
    if round_type == "coding" and not timed_out:
        language = request.data.get("language", "python")
        react_workspace = "react" in question.starter_code
        allowed_languages = ({"react"} if react_workspace
                             else {item["value"] for item in available_languages()})
        if language not in allowed_languages:
            return ApiResponse({"detail": "Unsupported language"}, status=400)
        code = request.data.get("code", "")
        results = (evaluate_react_solution(code, question.test_cases)
                   if react_workspace else run_code(code, language, question.test_cases))
        passed = sum(1 for result in results if result["passed"])
        response.code, response.language = code, language
        response.passed_tests, response.total_tests = passed, len(results)
        response.score = Decimal("10") * Decimal(passed) / max(1, len(results))
        response.is_correct = passed == len(results)
        attempt.passed_tests += passed
        attempt.total_tests += len(results)
    elif not timed_out:
        try: response.selected_option = int(request.data.get("selected_option"))
        except (TypeError, ValueError): response.selected_option = None
        response.is_correct = response.selected_option == question.correct_option
        response.score = 1 if response.is_correct else 0
    response.save()
    attempt.score += response.score
    advance(attempt)
    return ApiResponse({"accepted": True, "timed_out": timed_out, "state": attempt_state(attempt)})


@api_view(["POST"])
def try_code(request, round_type):
    candidate = candidate_for(request)
    attempt = Attempt.objects.filter(
        candidate=candidate,
        round_type=round_type,
        assessment_cycle=candidate.assessment_cycle,
    ).first()
    if not attempt or attempt.status != "in_progress":
        return ApiResponse({"detail": "This coding round is no longer active. Return to the assessment centre."}, status=409)
    question = cached_question(attempt.question_ids[attempt.current_index])
    if question.round_type != "coding": return ApiResponse({"detail": "Not a coding question"}, status=400)
    language = request.data.get("language", "python")
    react_workspace = "react" in question.starter_code
    allowed_languages = ({"react"} if react_workspace
                         else {item["value"] for item in available_languages()})
    if language not in allowed_languages: return ApiResponse({"detail": "Unsupported language"}, status=400)
    code = request.data.get("code", "")
    results = (evaluate_react_solution(code, question.test_cases[:question.visible_test_count])
               if react_workspace else run_code(code, language, question.test_cases[:question.visible_test_count]))
    return ApiResponse({"results": results})


@api_view(["POST"])
def admin_login(request):
    user = authenticate(username=request.data.get("username"), password=request.data.get("password"))
    if not user or not user.is_staff: return ApiResponse({"detail": "Invalid administrator credentials"}, status=401)
    return ApiResponse({"token": make_token(user.id, "admin"), "name": user.get_full_name() or user.username})


def require_admin(request):
    from django.contrib.auth import get_user_model
    return get_object_or_404(get_user_model(), id=read_token(request, "admin"), is_staff=True)


@api_view(["GET"])
def admin_dashboard(request):
    require_admin(request)
    candidates = list(Candidate.objects.prefetch_related("attempts").order_by("-registered_at"))
    rows = []
    for candidate in candidates:
        item = candidate_data(candidate, include_results=True)
        item["total_score"] = sum(round_result["score"] for round_result in item["rounds"])
        item["total_max"] = sum(round_result["max_score"] for round_result in item["rounds"])
        item["percentage"] = round(
            100 * item["total_score"] / item["total_max"], 1
        ) if item["total_max"] else 0
        rows.append(item)
    return ApiResponse({
        "summary": {"registered": len(rows), "completed": sum(1 for r in rows if r["status"] == "completed")},
        "candidates": rows,
    })


@api_view(["GET"])
def admin_candidate(request, candidate_id):
    require_admin(request)
    return ApiResponse(candidate_data(get_object_or_404(Candidate, id=candidate_id), detailed=True, include_results=True))


@api_view(["DELETE"])
def admin_candidate_delete(request, candidate_id):
    require_admin(request)
    deleted = delete_candidates(Candidate.objects.filter(id=candidate_id))
    if not deleted:
        return ApiResponse({"detail": "Not found."}, status=404)
    return ApiResponse({"deleted": True})


@api_view(["DELETE"])
def admin_selected_delete_all(request):
    require_admin(request)
    count = delete_candidates(Candidate.objects.filter(hiring_status="selected"))
    return ApiResponse({"deleted": count})


@api_view(["DELETE"])
def admin_rejected_delete_all(request):
    require_admin(request)
    try:
        batch_size = min(max(int(request.query_params.get("limit", "10")), 1), 50)
    except ValueError:
        return ApiResponse({"detail": "Invalid deletion batch size."}, status=400)

    deleted = delete_candidates(
        Candidate.objects.filter(hiring_status="rejected"), limit=batch_size
    )
    remaining = Candidate.objects.filter(hiring_status="rejected").count()
    return ApiResponse({"deleted": deleted, "remaining": remaining})


@api_view(["POST"])
def admin_candidate_reset(request, candidate_id):
    admin_user = require_admin(request)
    with transaction.atomic():
        candidate = get_object_or_404(Candidate.objects.select_for_update(), id=candidate_id)
        AssessmentReset.objects.create(
            candidate=candidate,
            assessment_cycle=candidate.assessment_cycle,
            status_before_reset=candidate.status,
            reset_by=admin_user,
        )
        candidate.assessment_cycle += 1
        candidate.status = "registered"
        candidate.access_locked = False
        candidate.completed_at = None
        candidate.hiring_status = "assessment_pending"
        candidate.hiring_status_updated_at = timezone.now()
        candidate.ai_rejection_reason = ""
        candidate.ai_rejected_at = None
        candidate.save(update_fields=[
            "assessment_cycle", "status", "access_locked", "completed_at",
            "hiring_status", "hiring_status_updated_at", "ai_rejection_reason",
            "ai_rejected_at",
        ])
    return ApiResponse({
        "reset": True,
        "candidate": candidate_data(candidate, detailed=True, include_results=True),
    })


@api_view(["PATCH"])
def admin_candidate_status(request, candidate_id):
    admin_user = require_admin(request)
    candidate = get_object_or_404(Candidate, id=candidate_id)
    new_status = request.data.get("hiring_status", "")
    if new_status not in dict(Candidate.HIRING_STATUS_CHOICES):
        return ApiResponse({"detail": "Invalid recruitment status"}, status=400)
    old_status = candidate.hiring_status
    candidate.hiring_status = new_status
    candidate.hiring_status_updated_at = timezone.now()
    candidate.save(update_fields=["hiring_status", "hiring_status_updated_at"])
    CandidateStatusHistory.objects.create(
        candidate=candidate, from_status=old_status, to_status=new_status,
        note=str(request.data.get("note", "")).strip()[:1000], changed_by=admin_user,
    )
    return ApiResponse({"candidate": candidate_data(candidate, detailed=True, include_results=True)})
