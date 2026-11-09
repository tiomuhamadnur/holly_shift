"""Tests for the user management UI and Super Admin floor (P1-T10, P1-T11)."""
import pytest
from django.core.management import call_command
from django.urls import reverse

from apps.accounts.models import Role, User
from apps.audit.models import AuditLog


@pytest.fixture
def roles(db):
    call_command("seed_roles")
    return {
        code: Role.objects.get(code=code)
        for code in ("super_admin", "admin", "teknisi")
    }


@pytest.fixture
def manager(client, roles):
    user = User.objects.create_superuser(
        username="root", email="root@example.com", password="S3cretPass!"
    )
    client.force_login(user)
    return client


def user_payload(role, **overrides):
    payload = {
        "username": "teknisi1",
        "first_name": "Budi",
        "last_name": "",
        "email": "budi@example.com",
        "role": role.pk,
        "language": "id",
        "theme": "system",
        "is_active": "on",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_user_list_requires_login(client):
    response = client.get(reverse("user_list"))

    assert response.status_code == 302
    assert reverse("login") in response["Location"]


def test_user_list_denies_without_permission(client, db):
    user = User.objects.create_user(username="plain", password="S3cretPass!")
    client.force_login(user)

    response = client.get(reverse("user_list"))

    assert response.status_code == 403


def test_user_list_shows_accounts(manager):
    response = manager.get(reverse("user_list"))

    assert response.status_code == 200
    assert b"root" in response.content


def test_create_user_sets_temporary_password(manager, roles):
    response = manager.post(
        reverse("user_create"),
        user_payload(roles["teknisi"], password="S3cretPass!"),
    )

    assert response.status_code == 302
    user = User.objects.get(username="teknisi1")
    assert user.role_id == roles["teknisi"].pk
    assert user.must_change_password is True
    assert user.check_password("S3cretPass!")
    assert AuditLog.objects.filter(
        action=AuditLog.Action.CREATE, entity="User", entity_id=str(user.pk)
    ).exists()


def test_create_user_rejects_weak_password(manager, roles):
    response = manager.post(
        reverse("user_create"),
        user_payload(roles["teknisi"], password="123"),
    )

    assert response.status_code == 200
    assert response.context["form"].errors["password"]
    assert not User.objects.filter(username="teknisi1").exists()


def test_update_user_changes_role_and_status(manager, roles):
    user = User.objects.create_user(
        username="teknisi1", password="S3cretPass!", role=roles["teknisi"]
    )

    response = manager.post(
        reverse("user_update", args=[user.pk]),
        user_payload(roles["admin"], email="", is_active="", language="en", theme="dark"),
    )

    assert response.status_code == 302
    user.refresh_from_db()
    assert user.role_id == roles["admin"].pk
    assert user.is_active is False
    entry = AuditLog.objects.filter(
        action=AuditLog.Action.UPDATE, entity="User", entity_id=str(user.pk)
    ).first()
    assert entry is not None
    assert entry.before["role"] == "teknisi"
    assert entry.after["role"] == "admin"


def test_last_super_admin_cannot_be_deactivated(manager, roles):
    target = User.objects.create_user(
        username="sa", password="S3cretPass!", role=roles["super_admin"]
    )

    response = manager.post(
        reverse("user_update", args=[target.pk]),
        user_payload(roles["super_admin"], username="sa", is_active=""),
    )

    assert response.status_code == 200
    assert response.context["form"].non_field_errors()
    target.refresh_from_db()
    assert target.is_active is True


def test_last_super_admin_cannot_change_role(manager, roles):
    target = User.objects.create_user(
        username="sa", password="S3cretPass!", role=roles["super_admin"]
    )

    response = manager.post(
        reverse("user_update", args=[target.pk]),
        user_payload(roles["admin"], username="sa"),
    )

    assert response.status_code == 200
    assert response.context["form"].non_field_errors()
    target.refresh_from_db()
    assert target.role_id == roles["super_admin"].pk


def test_super_admin_can_be_deactivated_when_another_remains(manager, roles):
    first = User.objects.create_user(
        username="sa1", password="S3cretPass!", role=roles["super_admin"]
    )
    User.objects.create_user(
        username="sa2", password="S3cretPass!", role=roles["super_admin"]
    )

    response = manager.post(
        reverse("user_update", args=[first.pk]),
        user_payload(roles["super_admin"], username="sa1", is_active=""),
    )

    assert response.status_code == 302
    first.refresh_from_db()
    assert first.is_active is False


def test_reset_password_forces_change(manager, roles):
    user = User.objects.create_user(
        username="teknisi1", password="S3cretPass!", role=roles["teknisi"]
    )

    response = manager.post(
        reverse("user_password_reset", args=[user.pk]),
        {"new_password": "N3wSecret!x"},
    )

    assert response.status_code == 302
    user.refresh_from_db()
    assert user.must_change_password is True
    assert user.check_password("N3wSecret!x")
    entry = AuditLog.objects.filter(
        action=AuditLog.Action.UPDATE, entity="User", entity_id=str(user.pk)
    ).first()
    assert entry is not None
    assert entry.after["password_reset"] is True


def test_reset_password_rejects_weak_value(manager, roles):
    user = User.objects.create_user(
        username="teknisi1", password="S3cretPass!", role=roles["teknisi"]
    )

    response = manager.post(
        reverse("user_password_reset", args=[user.pk]), {"new_password": "123"}
    )

    assert response.status_code == 200
    assert response.context["form"].errors["new_password"]


def test_inactive_user_cannot_login(client, roles):
    User.objects.create_user(
        username="off",
        password="S3cretPass!",
        role=roles["teknisi"],
        is_active=False,
    )

    client.post(reverse("login"), {"username": "off", "password": "S3cretPass!"})

    assert "_auth_user_id" not in client.session
