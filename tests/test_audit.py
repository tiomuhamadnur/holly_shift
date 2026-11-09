"""Tests for audit recording and auth integration (P1-T12)."""
import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.audit.services import record


@pytest.fixture
def user(db):
    return User.objects.create_user(username="budi", password="S3cretPass!")


@pytest.mark.django_db
def test_record_stores_before_after_and_ip(rf):
    request = rf.get("/x", REMOTE_ADDR="10.1.2.3")

    entry = record(
        None,
        AuditLog.Action.UPDATE,
        "Job",
        7,
        before={"status": "Belum"},
        after={"status": "Sedang"},
        request=request,
    )

    assert entry.ip == "10.1.2.3"
    assert entry.before == {"status": "Belum"}
    assert entry.after == {"status": "Sedang"}
    assert entry.entity == "Job"
    assert entry.entity_id == "7"
    assert entry.user is None


@pytest.mark.django_db
def test_record_prefers_forwarded_ip(rf):
    request = rf.get(
        "/x", HTTP_X_FORWARDED_FOR="203.0.113.9, 10.0.0.1", REMOTE_ADDR="10.0.0.1"
    )

    entry = record(None, AuditLog.Action.CREATE, "Job", 1, request=request)

    assert entry.ip == "203.0.113.9"


def test_successful_login_is_audited(client, user):
    client.post(reverse("login"), {"username": "budi", "password": "S3cretPass!"})

    log = AuditLog.objects.filter(action=AuditLog.Action.LOGIN).first()

    assert log is not None
    assert log.user_id == user.pk
    assert log.entity == "User"
    assert log.entity_id == str(user.pk)


def test_failed_login_is_audited(client, user):
    client.post(reverse("login"), {"username": "budi", "password": "wrong"})

    log = AuditLog.objects.filter(action=AuditLog.Action.LOGIN_FAILED).first()

    assert log is not None
    assert log.user is None
    assert log.entity_id == "budi"


def test_logout_is_audited(client, user):
    client.force_login(user)

    client.post(reverse("logout"))

    assert AuditLog.objects.filter(action=AuditLog.Action.LOGOUT, user=user).exists()
