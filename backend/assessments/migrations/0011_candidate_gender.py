from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessments", "0010_cleanup_orphaned_candidate_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="candidate",
            name="gender",
            field=models.CharField(
                choices=[
                    ("male", "Male"),
                    ("female", "Female"),
                    ("other", "Other"),
                    ("prefer_not_say", "Prefer not to say"),
                ],
                default="prefer_not_say",
                max_length=20,
            ),
        ),
    ]
