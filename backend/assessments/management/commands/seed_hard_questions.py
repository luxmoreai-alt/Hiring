import random
from django.core.management.base import BaseCommand
from assessments.models import Candidate, Question


APTITUDE = [
    ("quantitative", "A vessel contains milk and water in the ratio 7:3. Ten litres are removed and replaced by water; the ratio becomes 7:5. What was the original volume?", ["40 L", "50 L", "60 L", "70 L"], 2),
    ("quantitative", "If log₂(x) + log₄(x) = 15, then x equals:", ["256", "512", "1024", "2048"], 2),
    ("quantitative", "A train crosses a pole in 18 seconds and a 240 m platform in 30 seconds. Its speed is:", ["54 km/h", "60 km/h", "72 km/h", "80 km/h"], 2),
    ("logical", "Exactly one of P and Q is true. Q implies R, and R is false. Which statement must be true?", ["P is true", "Q is true", "P is false", "R is true"], 0),
    ("logical", "In a group, every architect is a designer, no designer is an auditor, and some auditors are managers. Which is impossible?", ["An architect is an auditor", "A manager is a designer", "An auditor is a manager", "A designer is a manager"], 0),
    ("logical", "Find the next term: 1, 2, 6, 15, 31, 56, ?", ["82", "87", "92", "96"], 2),
    ("verbal", "Choose the sentence with correct parallel structure.", ["She likes designing, to code, and testing.", "She likes to design, coding, and tests.", "She likes designing, coding, and testing.", "She likes design, to code, and testing."], 2),
    ("verbal", "The evidence was ___: it appeared persuasive, but collapsed under scrutiny.", ["incontrovertible", "specious", "redundant", "empirical"], 1),
    ("verbal", "Which inference is valid? 'Only candidates who pass coding reach the panel. Mira reached the panel.'", ["Mira passed coding", "Mira topped coding", "Everyone passed coding", "Mira skipped aptitude"], 0),
    ("non-verbal", "A cube is painted on all faces and cut into 64 equal cubes. How many small cubes have exactly two painted faces?", ["8", "16", "24", "32"], 2),
    ("non-verbal", "A 5×5 grid has both diagonals shaded. How many cells are shaded?", ["5", "8", "9", "10"], 2),
    ("non-verbal", "How many rectangles are present in a 3×4 rectangular grid?", ["36", "48", "60", "72"], 2),
]

TECHNICAL = [
    ("Under snapshot isolation, which anomaly can still occur without additional conflict detection?", "Write skew", ["Dirty read", "Non-repeatable read", "Lost acknowledgement"]),
    ("For a comparison sort, the worst-case lower bound is:", "Ω(n log n)", ["Ω(n)", "Ω(log n)", "Ω(n²)"]),
    ("Which property lets a distributed operation be retried safely after an ambiguous timeout?", "Idempotency", ["Locality", "Commutativity only", "Memoization"]),
    ("A Bloom filter can return:", "False positives but not false negatives", ["False negatives only", "Neither kind of error", "Both errors equally"]),
    ("Consistent hashing primarily reduces:", "Key remapping when nodes change", ["Hash computation", "TLS handshakes", "Transaction isolation"]),
    ("Which technique prevents stale cache writes from overwriting newer values?", "Version or fencing tokens", ["Longer TTL alone", "Round-robin DNS", "Gzip compression"]),
]

CODING = (
    "Minimum Meeting Rooms",
    "Read n followed by n start/end intervals. Print the minimum number of rooms required so no overlapping meetings share a room. End time equal to another start time does not overlap.",
    [{"input": "3\n0 30\n5 10\n15 20\n", "output": "2"}, {"input": "3\n7 10\n2 4\n10 12\n", "output": "1"}, {"input": "4\n1 5\n2 6\n3 7\n4 8\n", "output": "4"}],
)


class Command(BaseCommand):
    help = "Add advanced randomized questions without replacing the existing bank"

    def handle(self, *args, **options):
        for category, prompt, answers, correct in APTITUDE:
            Question.objects.update_or_create(prompt=prompt, defaults={"round_type": "aptitude", "category": category, "options": answers, "correct_option": correct, "active": True})
        rng = random.Random(2026)
        for role, _label in Candidate.ROLE_CHOICES:
            for prompt, correct, wrong in TECHNICAL:
                answers = [correct, *wrong]
                rng.shuffle(answers)
                Question.objects.update_or_create(prompt=prompt, role=role, defaults={"round_type": "technical", "category": "technical", "options": answers, "correct_option": answers.index(correct), "active": True})
            title, description, tests = CODING
            prompt = f"{title}\n\n{description}\n\nWrite a complete program that reads from standard input and writes to standard output."
            Question.objects.update_or_create(prompt=prompt, role=role, defaults={"round_type": "coding", "category": "coding", "starter_code": {"python": "# Implement an O(n log n) solution\n", "javascript": "// Implement an O(n log n) solution\n"}, "test_cases": tests, "visible_test_count": 2, "active": True})
        self.stdout.write(self.style.SUCCESS("Advanced question pools are ready"))
