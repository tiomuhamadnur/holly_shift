"""System settings service: read singleton and audit updates (FR-SET)."""
from django.db import transaction

from apps.audit.models import AuditLog
from apps.audit.services import record

from .models import SystemSetting

SNAPSHOT_FIELDS = (
    "retention_jobs_months",
    "retention_photos_months",
    "retention_audit_months",
    "retention_action",
    "dashboard_refresh_seconds",
    "display_mode",
    "default_language",
    "default_theme",
    "max_photo_kb",
    "max_import_mb",
    "idle_timeout_seconds",
)


def get_settings() -> SystemSetting:
    """Return the singleton settings row (created with defaults if needed)."""
    return SystemSetting.load()


def _snapshot(settings: SystemSetting) -> dict:
    return {field: getattr(settings, field) for field in SNAPSHOT_FIELDS}


@transaction.atomic
def update_settings(settings_obj: SystemSetting, *, data: dict, actor=None, request=None):
    """Apply validated settings and write a SETTING_CHANGE audit entry."""
    original = SystemSetting.objects.get(pk=settings_obj.pk)
    before = _snapshot(original)
    for field in SNAPSHOT_FIELDS:
        setattr(settings_obj, field, data[field])
    settings_obj.save()
    record(
        actor,
        AuditLog.Action.SETTING_CHANGE,
        "SystemSetting",
        settings_obj.pk,
        before=before,
        after=_snapshot(settings_obj),
        request=request,
    )
    return settings_obj
