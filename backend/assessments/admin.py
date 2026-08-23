from django.contrib import admin
from .models import AssessmentReset, Attempt, Candidate, CandidateStatusHistory, ProctorEvent, ProctorRecording, ProctorRecordingChunk, Question, Response

admin.site.register([Candidate, CandidateStatusHistory, AssessmentReset, Question, Attempt, Response, ProctorEvent, ProctorRecording, ProctorRecordingChunk])

# Register your models here.
