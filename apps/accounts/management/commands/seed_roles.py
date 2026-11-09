"""Seed the permission catalog and built-in roles. Idempotent."""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.catalog import PERMISSION_CATALOG, ROLE_SEEDS
from apps.accounts.models import Permission, Role


class Command(BaseCommand):
    help = "Seed the initial permission catalog and built-in roles (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        permissions = {}
        for item in PERMISSION_CATALOG:
            perm, _ = Permission.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "module": item["module"],
                    "is_implemented": item.get("is_implemented", True),
                },
            )
            permissions[item["code"]] = perm

        for seed in ROLE_SEEDS:
            role, _ = Role.objects.update_or_create(
                code=seed["code"],
                defaults={
                    "name": seed["name"],
                    "is_system": True,
                    "is_super_admin": seed.get("is_super_admin", False),
                },
            )
            if seed["permissions"] == "*":
                role.permissions.set(permissions.values())
            else:
                role.permissions.set([permissions[code] for code in seed["permissions"]])

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(permissions)} permissions and {len(ROLE_SEEDS)} roles."
            )
        )
