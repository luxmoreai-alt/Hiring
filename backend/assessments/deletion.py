from django.db import transaction

from .models import (
    AssessmentReset,
    Attempt,
    Candidate,
    CandidateStatusHistory,
    ProctorEvent,
    ProctorRecording,
    ProctorRecordingChunk,
    Response,
)


def delete_candidates(queryset, *, limit=None):
    """Delete candidates and every candidate-owned row in dependency order.

    Recording chunks and resumes can contain large binary values. Deleting the
    leaves explicitly keeps Django's cascade collector from loading a large
    candidate graph into memory in one serverless request.
    """
    with transaction.atomic():
        candidates = queryset.select_for_update().order_by("id")
        if limit is not None:
            candidates = candidates[:limit]
        candidate_ids = list(candidates.values_list("id", flat=True))
        if not candidate_ids:
            return 0

        recording_ids = ProctorRecording.objects.filter(
            candidate_id__in=candidate_ids
        ).values_list("id", flat=True)
        ProctorRecordingChunk.objects.filter(recording_id__in=recording_ids).delete()
        ProctorRecording.objects.filter(candidate_id__in=candidate_ids).delete()

        ProctorEvent.objects.filter(candidate_id__in=candidate_ids).delete()
        Response.objects.filter(attempt__candidate_id__in=candidate_ids).delete()
        Attempt.objects.filter(candidate_id__in=candidate_ids).delete()
        CandidateStatusHistory.objects.filter(candidate_id__in=candidate_ids).delete()
        AssessmentReset.objects.filter(candidate_id__in=candidate_ids).delete()

        # Resume bytes and AI rejection details live on the candidate row itself.
        Candidate.objects.filter(id__in=candidate_ids).delete()
        return len(candidate_ids)
