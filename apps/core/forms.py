"""System settings form for Super Admins (FR-SET-01, FR-SET-03)."""
from django import forms

from .models import SystemSetting


class SystemSettingForm(forms.ModelForm):
    class Meta:
        model = SystemSetting
        fields = [
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
        ]
