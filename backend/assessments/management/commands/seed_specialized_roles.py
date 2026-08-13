import random
from django.core.management.base import BaseCommand
from assessments.models import Question


BACKEND_MCQS = [
    ("Which HTTP method is normally used for a partial resource update?", "PATCH", ["GET", "HEAD", "OPTIONS"]),
    ("A database index primarily improves:", "Read and lookup performance", ["Password strength", "Network encryption", "Source formatting"]),
    ("Which Django component maps URLs to view functions?", "URL configuration", ["Template filter", "Migration executor", "Static collector"]),
    ("In REST, a 201 response normally means:", "A resource was created", ["Authentication failed", "Resource was deleted", "Server crashed"]),
    ("Connection pooling helps by:", "Reusing established database connections", ["Duplicating every query", "Removing transactions", "Encrypting source code"]),
    ("A database transaction should satisfy which properties?", "ACID", ["SOLID", "CRUD", "CAPTCHA"]),
    ("Caching is most useful for data that is:", "Read frequently and changes predictably", ["Always unique and secret", "Never requested", "Only written once then deleted"]),
    ("A foreign key is used to:", "Maintain relationships between tables", ["Compile code", "Route HTTP traffic", "Style a page"]),
    ("Which practice protects stored user passwords?", "Salted adaptive hashing", ["Base64 encoding", "Plain text storage", "Client-side hiding"]),
    ("An ORM maps:", "Objects to relational database records", ["CSS to HTML", "IP addresses to domains", "Files to CPU cores"]),
    ("A message queue helps services by:", "Decoupling asynchronous work", ["Removing all persistence", "Replacing authentication", "Rendering CSS"]),
    ("The N+1 query problem causes:", "Many unnecessary database queries", ["A DNS loop", "A compiler error", "A stronger index"]),
    ("JWT signatures primarily provide:", "Token integrity and issuer verification", ["Database encryption", "Password recovery", "UI responsiveness"]),
    ("Rate limiting protects an API from:", "Excessive request volume", ["Valid JSON", "Database indexes", "Semantic HTML"]),
    ("Which status code indicates a conflict with current resource state?", "409", ["200", "204", "301"]),
    ("Idempotency means repeating the same operation:", "Has no additional effect after the first successful call", ["Always creates a new row", "Always fails", "Skips validation"]),
    ("Database normalization mainly reduces:", "Redundancy and update anomalies", ["TLS latency", "CPU instructions", "API documentation"]),
    ("A health-check endpoint is used to:", "Report whether a service can receive traffic", ["Reset every password", "Compile frontend code", "Create database schemas"]),
    ("Environment variables are commonly used for:", "Deployment-specific configuration", ["Permanent user content", "HTML structure", "Database joins"]),
    ("Which test verifies several backend components working together?", "Integration test", ["Unit test only", "Typography test", "Snapshot of CSS only"]),
]

BACKEND_CODING = [
    ("API Endpoint Summary", "Read n, followed by n lines containing endpoint and HTTP status. For each endpoint, print: endpoint success_count failure_count. A status from 200 to 399 is successful. Output endpoints in lexicographic order.", ["5\n/users 200\n/login 401\n/users 201\n/login 200\n/orders 500\n", "3\n/a 200\n/a 404\n/a 302\n", "2\n/z 500\n/a 500\n"], ["/login 1 1\n/orders 0 1\n/users 2 0", "/a 2 1", "/a 0 1\n/z 0 1"]),
    ("Merge Request Windows", "Read n time intervals (start end). Merge every overlapping interval and print the merged intervals in ascending order, one per line.", ["4\n1 3\n2 6\n8 10\n9 12\n", "3\n1 2\n3 4\n5 6\n", "4\n1 10\n2 3\n4 8\n11 12\n"], ["1 6\n8 12", "1 2\n3 4\n5 6", "1 10\n11 12"]),
]


class Command(BaseCommand):
    help = "Create independent Frontend, Backend, and Full Stack assessment banks"

    def handle(self, *args, **options):
        target_roles = ["frontend-developer", "backend-developer", "full-stack-developer"]
        Question.objects.filter(role__in=target_roles).delete()
        rng = random.Random(2026)

        frontend_source = list(Question.objects.filter(role="web-developer", round_type="technical", active=True).order_by("id")[:20])
        if len(frontend_source) < 20:
            raise RuntimeError("The Web Developer bank must contain 20 questions first")
        frontend_questions = []
        for source in frontend_source:
            frontend_questions.append(Question.objects.create(
                round_type="technical", category="technical", role="frontend-developer",
                prompt=source.prompt, options=source.options, correct_option=source.correct_option,
                explanation=source.explanation,
            ))

        backend_questions = []
        for prompt, correct, wrong in BACKEND_MCQS:
            answers = wrong + [correct]
            rng.shuffle(answers)
            backend_questions.append(Question.objects.create(
                round_type="technical", category="technical", role="backend-developer",
                prompt=prompt, options=answers, correct_option=answers.index(correct),
            ))

        for source in frontend_questions[:10] + backend_questions[:10]:
            Question.objects.create(
                round_type="technical", category="technical", role="full-stack-developer",
                prompt=source.prompt, options=source.options, correct_option=source.correct_option,
                explanation=source.explanation,
            )

        frontend_coding = list(Question.objects.filter(role="web-developer", round_type="coding", active=True).order_by("id")[:2])
        for source in frontend_coding:
            Question.objects.create(
                round_type="coding", category="coding", role="frontend-developer", prompt=source.prompt,
                starter_code=source.starter_code, test_cases=source.test_cases,
                visible_test_count=source.visible_test_count,
            )
        backend_created = []
        for title, description, inputs, outputs in BACKEND_CODING:
            backend_created.append(Question.objects.create(
                round_type="coding", category="coding", role="backend-developer",
                prompt=f"{title}\n\n{description}\n\nWrite a complete program that reads from standard input and writes to standard output.",
                starter_code={"python": "# Read from standard input and print the answer\n", "javascript": "// Read stdin and print the answer\n"},
                test_cases=[{"input": value, "output": outputs[index]} for index, value in enumerate(inputs)],
                visible_test_count=2,
            ))
        for source in [frontend_coding[0], backend_created[0]]:
            Question.objects.create(
                round_type="coding", category="coding", role="full-stack-developer", prompt=source.prompt,
                starter_code=source.starter_code, test_cases=source.test_cases,
                visible_test_count=source.visible_test_count,
            )
        self.stdout.write(self.style.SUCCESS("Seeded 66 specialized role questions"))
