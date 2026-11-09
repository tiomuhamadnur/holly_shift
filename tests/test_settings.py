"""Tests for system settings and middleware (P1-T14)."""
import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.accounts.forms import ProfileForm
from apps.accounts.models import Permission, Role, User
from apps.audit.models import AuditLog
from apps.core.models import SystemSetting


@pytest.fixture
def settings_row(db):
    return SystemSetting.load()


@pytest.fixture
def manager(db):
    permission = Permission.objects.create(
        code="settings.manage", name="Manage settings"
    )
    role = Role.objects.create(code="manager", name="Manager")
    role.permissions.add(permission)
    return User.objects.create_user(username="manager", password="S3cretPass!", role=role)


@pytest.fixture
def manager_client(client, manager):
    client.force_login(manager)
    return client


def settings_payload(**overrides):
    payload = {
        "retention_jobs_months": 12,
        "retention_photos_months": 12,
        "retention_audit_months": 24,
        "retention_action": "archive_delete",
        "dashboard_refresh_seconds": 15,
        "display_mode": "dark",
        "default_language": "id",
        "default_theme": "system",
        "max_photo_kb": 300,
        "max_import_mb": 10,
        "idle_timeout_seconds": 43200,
    }
    payload.update(overrides)
    return payload


def test_load_creates_singleton(settings_row):
    assert settings_row.pk == 1
    assert SystemSetting.load().pk == 1
    assert SystemSetting.objects.count() == 1


@pytest.mark.django_db
def test_settings_view_requires_login(client):
    response = client.get(reverse("settings"))

    assert response.status_code == 302


def test_settings_view_denies_without_permission(client, db):
    user = User.objects.create_user(username="plain", password="S3cretPass!")
    client.force_login(user)

    response = client.get(reverse("settings"))

    assert response.status_code == 403


def test_update_settings_writes_audit(manager_client, settings_row):
    response = manager_client.post(
        reverse("settings"),
        settings_payload(dashboard_refresh_seconds=30, default_language="en"),
    )

    assert response.status_code == 302
    settings_row.refresh_from_db()
    assert settings_row.dashboard_refresh_seconds == 30
    assert settings_row.default_language == "en"
    entry = AuditLog.objects.filter(
        action=AuditLog.Action.SETTING_CHANGE, entity="SystemSetting"
    ).first()
    assert entry is not None
    assert entry.before["dashboard_refresh_seconds"] == 15
    assert entry.after["dashboard_refresh_seconds"] == 30


def test_invalid_refresh_interval_is_rejected(manager_client, settings_row):
    response = manager_client.post(
        reverse("settings"), settings_payload(dashboard_refresh_seconds=1)
    )

    assert response.status_code == 200
    assert response.context["form"].errors["dashboard_refresh_seconds"]
    settings_row.refresh_from_db()
    assert settings_row.dashboard_refresh_seconds == 15


def test_idle_timeout_middleware_applies_setting(client, manager, settings_row):
    settings_row.idle_timeout_seconds = 600
    settings_row.save()
    client.force_login(manager)

    client.get("/")

    assert 590 <= client.session.get_expiry_age() <= 601


def test_anonymous_uses_default_language(client, settings_row):
    settings_row.default_language = "en"
    settings_row.save()

    response = client.get("/")

    assert response.headers["Content-Language"] == "en"


def test_photo_limit_uses_setting(settings_row):
    settings_row.max_photo_kb = 1
    settings_row.save()

    class Oversize:
        size = 2048

    form = ProfileForm()
    form.cleaned_data = {"photo": Oversize()}

    with pytest.raises(ValidationError):
        form.clean_photo()
