"""Tests for the custom user, role and permission models (P1-T01, P1-T07)."""
import pytest
from django.db import IntegrityError, transaction

from apps.accounts.models import Permission, Role, User


@pytest.mark.django_db
def test_create_user_with_username_only():
    user = User.objects.create_user(username="teknisi1", password="S3cretPass!")

    assert user.pk is not None
    assert user.email == ""
    assert user.language == "id"
    assert user.theme == User.Theme.SYSTEM
    assert user.is_active is True
    assert user.has_perm_code("anything") is False


@pytest.mark.django_db
def test_email_is_optional_and_unique_when_present():
    User.objects.create_user(username="a", email="a@example.com", password="S3cretPass!")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            User.objects.create_user(username="b", email="a@example.com", password="S3cretPass!")


@pytest.mark.django_db
def test_multiple_users_may_have_empty_email():
    first = User.objects.create_user(username="c", password="S3cretPass!")
    second = User.objects.create_user(username="d", password="S3cretPass!")

    assert first.email == ""
    assert second.email == ""


@pytest.mark.django_db
def test_has_perm_code_uses_role_permissions():
    view_job = Permission.objects.create(code="job.view", name="View jobs")
    Role.objects.create(code="teknisi", name="Teknisi").permissions.add(view_job)
    role = Role.objects.get(code="teknisi")
    user = User.objects.create_user(username="e", password="S3cretPass!", role=role)

    assert user.has_perm_code("job.view") is True
    assert user.has_perm_code("job.edit") is False
    assert user.permission_codes == {"job.view"}


@pytest.mark.django_db
def test_superuser_bypasses_permission_codes():
    user = User.objects.create_superuser(
        username="root", email="root@example.com", password="S3cretPass!"
    )

    assert user.has_perm_code("does.not.exist") is True


@pytest.mark.django_db
def test_user_str_prefers_full_name():
    user = User.objects.create_user(
        username="f", first_name="Budi", last_name="Santoso", password="S3cretPass!"
    )

    assert str(user) == "Budi Santoso"
