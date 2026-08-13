from django.core.management.base import BaseCommand
from django.utils import timezone

from assessments.management.commands.seed_specialized_roles import FRONTEND_CODING
from assessments.models import Attempt, Question, Response


class Command(BaseCommand):
    help = "Install the practical React coding challenges for frontend candidates."

    def handle(self, *args, **options):
        Question.objects.filter(
            role="frontend-developer", round_type="coding", active=True
        ).update(active=False)

        challenge_ids = []
        for challenge in FRONTEND_CODING:
            prompt = f"{challenge['title']}\n\n{challenge['description']}"
            question, _ = Question.objects.update_or_create(
                role="frontend-developer",
                round_type="coding",
                prompt=prompt,
                defaults={
                    "category": "coding",
                    "starter_code": {"react": challenge["starter"]},
                    "test_cases": challenge["tests"],
                    "visible_test_count": len(challenge["tests"]),
                    "active": True,
                },
            )
            challenge_ids.append(question.id)

        reset_count = 0
        attempts = Attempt.objects.filter(
            candidate__role="frontend-developer",
            round_type="coding",
            status="in_progress",
        )
        for attempt in attempts:
            if attempt.question_ids == challenge_ids:
                continue
            Response.objects.filter(attempt=attempt).delete()
            attempt.question_ids = challenge_ids
            attempt.current_index = 0
            attempt.question_started_at = timezone.now()
            attempt.score = 0
            attempt.max_score = 20
            attempt.passed_tests = 0
            attempt.total_tests = 0
            attempt.save(update_fields=[
                "question_ids", "current_index", "question_started_at", "score",
                "max_score", "passed_tests", "total_tests",
            ])
            reset_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Installed 2 React frontend challenges; reset {reset_count} active attempt(s)"
        ))
