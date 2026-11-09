"""Seed the singleton system settings row. Idempotent."""
from django.core.management.base import BaseCommand

from apps.core.models import SystemSetting


class Command(BaseCommand):
    help = "Create the singleton system settings row with defaults (idempotent)."

    def handle(self, *args, **options):
        settings = SystemSetting.load()
        self.stdout.write(
            self.style.SUCCESS(f"System settings ready (pk={settings.pk}).")
        )
