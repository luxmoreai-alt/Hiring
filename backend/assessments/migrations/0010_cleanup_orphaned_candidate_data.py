from django.db import migrations


def cleanup_orphaned_candidate_data(apps, schema_editor):
    """Remove legacy rows left by candidate deletions before full cleanup existed."""
    q = schema_editor.quote_name
    tables = {
        "candidate": "assessments_candidate",
        "attempt": "assessments_attempt",
        "response": "assessments_response",
        "event": "assessments_proctorevent",
        "history": "assessments_candidatestatushistory",
        "reset": "assessments_assessmentreset",
        "recording": "assessments_proctorrecording",
        "chunk": "assessments_proctorrecordingchunk",
    }

    def delete_where(table, condition):
        schema_editor.execute(f"DELETE FROM {q(table)} WHERE {condition}")

    candidate = q(tables["candidate"])
    attempt = q(tables["attempt"])
    recording = q(tables["recording"])

    # Delete binary leaves first. This also covers recordings whose candidate
    # or attempt disappeared while database FK enforcement was unavailable.
    chunk_table = q(tables["chunk"])
    delete_where(
        tables["chunk"],
        f"NOT EXISTS (SELECT 1 FROM {recording} r WHERE r.id = {chunk_table}.recording_id) "
        f"OR EXISTS (SELECT 1 FROM {recording} r WHERE r.id = {chunk_table}.recording_id "
        f"AND (NOT EXISTS (SELECT 1 FROM {candidate} c WHERE c.id = r.candidate_id) "
        f"OR NOT EXISTS (SELECT 1 FROM {attempt} a WHERE a.id = r.attempt_id)))",
    )

    recording_table = q(tables["recording"])
    delete_where(
        tables["recording"],
        f"NOT EXISTS (SELECT 1 FROM {candidate} c WHERE c.id = {recording_table}.candidate_id) "
        f"OR NOT EXISTS (SELECT 1 FROM {attempt} a WHERE a.id = {recording_table}.attempt_id)",
    )

    event_table = q(tables["event"])
    delete_where(
        tables["event"],
        f"NOT EXISTS (SELECT 1 FROM {candidate} c WHERE c.id = {event_table}.candidate_id) "
        f"OR ({event_table}.attempt_id IS NOT NULL AND NOT EXISTS "
        f"(SELECT 1 FROM {attempt} a WHERE a.id = {event_table}.attempt_id))",
    )

    response_table = q(tables["response"])
    delete_where(
        tables["response"],
        f"NOT EXISTS (SELECT 1 FROM {attempt} a WHERE a.id = {response_table}.attempt_id) "
        f"OR EXISTS (SELECT 1 FROM {attempt} a WHERE a.id = {response_table}.attempt_id "
        f"AND NOT EXISTS (SELECT 1 FROM {candidate} c WHERE c.id = a.candidate_id))",
    )

    attempt_table = q(tables["attempt"])
    delete_where(
        tables["attempt"],
        f"NOT EXISTS (SELECT 1 FROM {candidate} c WHERE c.id = {attempt_table}.candidate_id)",
    )

    for key in ("history", "reset"):
        table = q(tables[key])
        delete_where(
            tables[key],
            f"NOT EXISTS (SELECT 1 FROM {candidate} c WHERE c.id = {table}.candidate_id)",
        )


class Migration(migrations.Migration):
    dependencies = [("assessments", "0009_proctorrecording_kind")]

    operations = [
        migrations.RunPython(cleanup_orphaned_candidate_data, migrations.RunPython.noop),
    ]
