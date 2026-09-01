from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("assessments", "0008_candidate_resume_and_proctor_recording")]
    operations = [
        migrations.AddField(
            model_name="proctorrecording",
            name="kind",
            field=models.CharField(
                choices=[("camera", "Camera and microphone"), ("screen", "Screen")],
                default="camera",
                max_length=20,
            ),
        ),
    ]
