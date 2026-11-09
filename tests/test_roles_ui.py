"""Tests for the role management UI (P1-T09)."""
import pytest
from django.core.management import call_command
from django.urls import reverse

from apps.accounts.models import Permission, Role, User
from apps.audit.models import AuditLog


@pytest.fixture
def seeded(db):
    call_command("seed_roles")
    return Role.objects.get(code="super_admin")


@pytest.fixture
def admin_client(client, seeded):
    user = User.objects.create_superuser(
        username="root", email="root@example.com", password="S3cretPass!"
    )
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_role_list_requires_login(client):
    response = client.get(reverse("role_list"))

    assert response.status_code == 302
    assert reverse("login") in response["Location"]


def test_role_list_denies_without_permission(client, db):
    user = User.objects.create_user(username="plain", password="S3cretPass!")
    client.force_login(user)

    response = client.get(reverse("role_list"))

    assert response.status_code == 403


def test_role_list_shows_seeded_roles(admin_client):
    response = admin_client.get(reverse("role_list"))

    assert response.status_code == 200
    assert b"Super Admin" in response.content
    assert b"Teknisi" in response.content


def test_create_role_with_permissions(admin_client):
    permission = Permission.objects.get(code="job.view")

    response = admin_client.post(
        reverse("role_create"),
        {"name": "Planner", "description": "", "permissions": [permission.pk]},
    )

    assert response.status_code == 302
    role = Role.objects.get(name="Planner")
    assert role.code == "planner"
    assert list(role.permissions.values_list("code", flat=True)) == ["job.view"]
    assert AuditLog.objects.filter(
        action=AuditLog.Action.CREATE, entity="Role", entity_id=str(role.pk)
    ).exists()


def test_update_role_changes_permissions(admin_client):
    role = Role.objects.create(code="planner", name="Planner")
    permission = Permission.objects.get(code="job.view")

    response = admin_client.post(
        reverse("role_update", args=[role.pk]),
        {"name": "Planner", "description": "ops", "permissions": [permission.pk]},
    )

    assert response.status_code == 302
    role.refresh_from_db()
    assert role.description == "ops"
    assert list(role.permissions.values_list("code", flat=True)) == ["job.view"]
    entry = AuditLog.objects.filter(
        action=AuditLog.Action.UPDATE, entity="Role", entity_id=str(role.pk)
    ).first()
    assert entry is not None
    assert entry.before["permissions"] == []
    assert entry.after["permissions"] == ["job.view"]


def test_permission_change_applies_on_next_request(admin_client):
    role = Role.objects.create(code="planner", name="Planner")
    user = User.objects.create_user(username="planner", password="S3cretPass!", role=role)
    assert not user.has_perm_code("job.view")

    permission = Permission.objects.get(code="job.view")
    admin_client.post(
        reverse("role_update", args=[role.pk]),
        {"name": "Planner", "description": "", "permissions": [permission.pk]},
    )

    assert User.objects.get(pk=user.pk).has_perm_code("job.view")


def test_builtin_role_cannot_be_deleted(admin_client, seeded):
    response = admin_client.post(reverse("role_delete", args=[seeded.pk]))

    assert response.status_code == 302
    assert Role.objects.filter(pk=seeded.pk).exists()


def test_delete_custom_role(admin_client):
    role = Role.objects.create(code="temp", name="Temp")

    response = admin_client.post(reverse("role_delete", args=[role.pk]))

    assert response.status_code == 302
    assert not Role.objects.filter(pk=role.pk).exists()
    assert AuditLog.objects.filter(action=AuditLog.Action.DELETE, entity="Role").exists()


def test_delete_role_in_use_is_blocked(admin_client):
    role = Role.objects.create(code="used", name="Used")
    User.objects.create_user(username="member", password="S3cretPass!", role=role)

    response = admin_client.post(reverse("role_delete", args=[role.pk]))

    assert response.status_code == 302
    assert Role.objects.filter(pk=role.pk).exists()
