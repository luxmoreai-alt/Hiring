import django.db.models.deletion
from django.db import migrations, models


def normalize_colleges(apps, schema_editor):
    Candidate = apps.get_model("assessments", "Candidate")
    for candidate in Candidate.objects.all().iterator():
        normalized = " ".join(candidate.college.split()).casefold()
        candidate.college = " ".join(candidate.college.split())
        candidate.college_normalized = normalized
        candidate.save(update_fields=["college", "college_normalized"])


class Migration(migrations.Migration):
    dependencies = [("assessments", "0007_assessmentreset_and_more")]
    operations = [
        migrations.AddField(model_name="candidate", name="college_normalized", field=models.CharField(blank=True, db_index=True, max_length=200)),
        migrations.AddField(model_name="candidate", name="resume_name", field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name="candidate", name="resume_content_type", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="candidate", name="resume_size", field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name="candidate", name="resume_data", field=models.BinaryField(blank=True, null=True)),
        migrations.AddField(model_name="candidate", name="ai_rejection_reason", field=models.TextField(blank=True)),
        migrations.AddField(model_name="candidate", name="ai_rejected_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.CreateModel(
            name="ProctorRecording",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mime_type", models.CharField(default="video/webm", max_length=100)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("total_size", models.PositiveBigIntegerField(default=0)),
                ("chunk_count", models.PositiveIntegerField(default=0)),
                ("attempt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="recordings", to="assessments.attempt")),
                ("candidate", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="proctor_recordings", to="assessments.candidate")),
            ],
            options={"ordering": ["started_at"]},
        ),
        migrations.CreateModel(
            name="ProctorRecordingChunk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sequence", models.PositiveIntegerField()),
                ("data", models.BinaryField()),
                ("recording", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chunks", to="assessments.proctorrecording")),
            ],
            options={"ordering": ["sequence"]},
        ),
        migrations.AddConstraint(model_name="proctorrecordingchunk", constraint=models.UniqueConstraint(fields=("recording", "sequence"), name="unique_recording_chunk")),
        migrations.RunPython(normalize_colleges, migrations.RunPython.noop),
    ]
