import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the administrator configured through environment variables."

    def handle(self, *args, **options):
        username = os.getenv("ADMIN_USERNAME", "").strip()
        password = os.getenv("ADMIN_PASSWORD", "")

        if not username or not password:
            raise CommandError(
                "ADMIN_USERNAME and ADMIN_PASSWORD must be configured."
            )

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={"email": username if "@" in username else ""},
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        if "@" in username and not user.email:
            user.email = username
        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} administrator {username}."))
