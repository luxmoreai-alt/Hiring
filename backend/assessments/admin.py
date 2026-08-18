from django.contrib import admin
from .models import AssessmentReset, Attempt, Candidate, CandidateStatusHistory, ProctorEvent, Question, Response

admin.site.register([Candidate, CandidateStatusHistory, AssessmentReset, Question, Attempt, Response, ProctorEvent])

# Register your models here.
