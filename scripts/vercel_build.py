"""Prepare the Django application during a Vercel production build."""
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402
from django.core.management import call_command  # noqa: E402


django.setup()
call_command("migrate", interactive=False)
call_command("ensure_admin")
call_command("seed_frontend_challenges")
call_command("collectstatic", interactive=False)
