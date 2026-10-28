from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessments", "0012_normalize_candidate_names"),
    ]

    operations = [
        migrations.AddField(
            model_name="candidate",
            name="offer_studio_id",
            field=models.CharField(blank=True, db_index=True, max_length=64),
        ),
        migrations.AddField(
            model_name="candidate",
            name="offer_studio_created_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
