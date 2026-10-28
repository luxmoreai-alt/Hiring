from django.db import migrations


def normalize_candidate_names(apps, schema_editor):
    Candidate = apps.get_model("assessments", "Candidate")
    for candidate in Candidate.objects.only("id", "name").iterator():
        normalized_name = " ".join((candidate.name or "").split()).upper()
        if candidate.name != normalized_name:
            Candidate.objects.filter(id=candidate.id).update(name=normalized_name)


class Migration(migrations.Migration):
    dependencies = [
        ("assessments", "0011_candidate_gender"),
    ]

    operations = [
        migrations.RunPython(normalize_candidate_names, migrations.RunPython.noop),
    ]
