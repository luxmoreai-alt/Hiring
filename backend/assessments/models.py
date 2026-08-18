import uuid
from django.db import models


class Candidate(models.Model):
    ROLE_CHOICES = [
        ("data-analyst", "Data Analyst"),
        ("mern-stack-developer", "MERN Stack Developer"),
        ("frontend-developer", "Frontend Developer"),
        ("backend-developer", "Backend Developer"),
        ("full-stack-developer", "Full Stack Developer"),
        ("web-developer", "Web Developer"),
        ("cloud-engineer", "Cloud Engineer"),
    ]
    STATUS_CHOICES = [("registered", "Registered"), ("aptitude", "Aptitude"), ("technical", "Technical"), ("coding", "Coding"), ("completed", "Completed")]
    LOCATION_CHOICES = [("not_provided", "Not provided"), ("chennai", "Chennai"), ("bengaluru", "Bengaluru"), ("hyderabad", "Hyderabad")]
    HIRING_STATUS_CHOICES = [
        ("assessment_pending", "Assessment pending"),
        ("assessment_completed", "Assessment completed"),
        ("technical_scheduled", "Technical interview scheduled"),
        ("technical_completed", "Technical interview completed"),
        ("hr_scheduled", "HR interview scheduled"),
        ("hr_completed", "HR interview completed"),
        ("on_hold", "On hold"),
        ("selected", "Selected"),
        ("rejected", "Rejected"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    college = models.CharField(max_length=200)
    designation = models.CharField(max_length=120, help_text="Degree, department, or current designation")
    address = models.TextField()
    role = models.CharField(max_length=40, choices=ROLE_CHOICES)
    preferred_location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default="not_provided")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="registered")
    hiring_status = models.CharField(max_length=30, choices=HIRING_STATUS_CHOICES, default="assessment_pending")
    hiring_status_updated_at = models.DateTimeField(null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    assessment_cycle = models.PositiveIntegerField(default=1)
    access_locked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} — {self.get_role_display()}"


class Question(models.Model):
    ROUND_CHOICES = [("aptitude", "Aptitude"), ("technical", "Technical"), ("coding", "Coding")]
    CATEGORY_CHOICES = [("quantitative", "Quantitative"), ("logical", "Logical reasoning"), ("verbal", "Verbal ability"), ("non-verbal", "Non-verbal reasoning"), ("technical", "Technical"), ("coding", "Coding")]
    round_type = models.CharField(max_length=20, choices=ROUND_CHOICES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    role = models.CharField(max_length=40, choices=Candidate.ROLE_CHOICES, blank=True)
    prompt = models.TextField()
    options = models.JSONField(default=list, blank=True)
    correct_option = models.PositiveSmallIntegerField(null=True, blank=True)
    explanation = models.TextField(blank=True)
    starter_code = models.JSONField(default=dict, blank=True)
    test_cases = models.JSONField(default=list, blank=True)
    visible_test_count = models.PositiveSmallIntegerField(default=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.round_type}: {self.prompt[:70]}"


class Attempt(models.Model):
    STATUS_CHOICES = [("in_progress", "In progress"), ("completed", "Completed"), ("auto_submitted", "Auto submitted"), ("terminated", "Terminated after exit")]
    candidate = models.ForeignKey(Candidate, related_name="attempts", on_delete=models.CASCADE)
    round_type = models.CharField(max_length=20, choices=Question.ROUND_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_progress")
    question_ids = models.JSONField(default=list)
    current_index = models.PositiveIntegerField(default=0)
    question_started_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    max_score = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    passed_tests = models.PositiveIntegerField(default=0)
    total_tests = models.PositiveIntegerField(default=0)
    violation_count = models.PositiveIntegerField(default=0)
    assessment_cycle = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["started_at"]
        constraints = [models.UniqueConstraint(fields=["candidate", "round_type", "assessment_cycle"], name="unique_candidate_round_cycle")]


class Response(models.Model):
    attempt = models.ForeignKey(Attempt, related_name="responses", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.IntegerField(null=True, blank=True)
    code = models.TextField(blank=True)
    language = models.CharField(max_length=20, blank=True)
    is_correct = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    passed_tests = models.PositiveIntegerField(default=0)
    total_tests = models.PositiveIntegerField(default=0)
    timed_out = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["attempt", "question"], name="unique_attempt_response")]


class ProctorEvent(models.Model):
    candidate = models.ForeignKey(Candidate, related_name="proctor_events", on_delete=models.CASCADE)
    attempt = models.ForeignKey(Attempt, related_name="proctor_events", on_delete=models.CASCADE, null=True)
    event_type = models.CharField(max_length=40)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CandidateStatusHistory(models.Model):
    candidate = models.ForeignKey(Candidate, related_name="status_history", on_delete=models.CASCADE)
    from_status = models.CharField(max_length=30, blank=True)
    to_status = models.CharField(max_length=30, choices=Candidate.HIRING_STATUS_CHOICES)
    note = models.TextField(blank=True)
    changed_by = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class AssessmentReset(models.Model):
    candidate = models.ForeignKey(Candidate, related_name="assessment_resets", on_delete=models.CASCADE)
    assessment_cycle = models.PositiveIntegerField()
    status_before_reset = models.CharField(max_length=20)
    reset_by = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
