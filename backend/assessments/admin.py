from django.contrib import admin
from .models import Attempt, Candidate, CandidateStatusHistory, ProctorEvent, Question, Response

admin.site.register([Candidate, CandidateStatusHistory, Question, Attempt, Response, ProctorEvent])

# Register your models here.
