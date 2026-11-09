"""Tests for password policy, forced change and admin reset (P1-T03)."""
import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.accounts.models import User
from apps.accounts.services import set_temporary_password


@pytest.fixture
def user(db):
    return User.objects.create_user(username="budi", password="S3cretPass!")


def test_set_temporary_password_hashes_and_flags(user):
    set_temporary_password(user, "TempPass!234")

    user.refresh_from_db()
    assert user.must_change_password is True
    assert user.check_password("TempPass!234")
    assert "TempPass!234" not in user.password


@pytest.mark.parametrize("weak", ["123", "password", "short"])
def test_set_temporary_password_rejects_weak(user, weak):
    with pytest.raises(ValidationError):
        set_temporary_password(user, weak)


def test_password_change_updates_password_and_clears_flag(client, user):
    user.must_change_password = True
    user.save(update_fields=["must_change_password"])
    client.force_login(user)

    response = client.post(
        reverse("password_change"),
        {
            "old_password": "S3cretPass!",
            "new_password1": "N3wS3cret!pass",
            "new_password2": "N3wS3cret!pass",
        },
    )

    assert response.status_code == 302
    user.refresh_from_db()
    assert user.check_password("N3wS3cret!pass")
    assert user.must_change_password is False


def test_password_change_rejects_wrong_old_password(client, user):
    client.force_login(user)

    response = client.post(
        reverse("password_change"),
        {
            "old_password": "wrong",
            "new_password1": "N3wS3cret!pass",
            "new_password2": "N3wS3cret!pass",
        },
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("S3cretPass!")


def test_middleware_redirects_when_change_required(client, db):
    user = User.objects.create_user(
        username="temp", password="S3cretPass!", must_change_password=True
    )
    client.force_login(user)

    response = client.get("/")

    assert response.status_code == 302
    assert response.url == reverse("password_change")


def test_middleware_allows_normal_user(client, user):
    client.force_login(user)

    response = client.get("/")

    assert response.status_code == 200


def test_middleware_allows_password_change_page(client, db):
    user = User.objects.create_user(
        username="temp2", password="S3cretPass!", must_change_password=True
    )
    client.force_login(user)

    response = client.get(reverse("password_change"))

    assert response.status_code == 200


def test_middleware_allows_logout(client, db):
    user = User.objects.create_user(
        username="temp3", password="S3cretPass!", must_change_password=True
    )
    client.force_login(user)

    response = client.post(reverse("logout"))

    assert response.status_code == 302
    assert "_auth_user_id" not in client.session
