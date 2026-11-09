"""Tests for authentication: email/username login, logout, idle timeout (P1-T02)."""
import pytest
from django.conf import settings
from django.urls import reverse

from apps.accounts.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="budi", email="budi@example.com", password="S3cretPass!"
    )


@pytest.mark.django_db
def test_login_page_renders(client):
    response = client.get(reverse("login"))

    assert response.status_code == 200
    assert b"csrfmiddlewaretoken" in response.content


def test_login_with_username(client, user):
    response = client.post(
        reverse("login"), {"username": "budi", "password": "S3cretPass!"}
    )

    assert response.status_code == 302
    assert response.url == settings.LOGIN_REDIRECT_URL
    assert client.session["_auth_user_id"] == str(user.pk)


def test_login_with_email(client, user):
    response = client.post(
        reverse("login"), {"username": "budi@example.com", "password": "S3cretPass!"}
    )

    assert response.status_code == 302
    assert client.session["_auth_user_id"] == str(user.pk)


def test_login_is_case_insensitive(client, user):
    response = client.post(
        reverse("login"), {"username": "BUDI@EXAMPLE.COM", "password": "S3cretPass!"}
    )

    assert response.status_code == 302
    assert client.session["_auth_user_id"] == str(user.pk)


def test_login_with_wrong_password_fails(client, user):
    response = client.post(reverse("login"), {"username": "budi", "password": "wrong"})

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_login_inactive_user_fails(client, db):
    User.objects.create_user(username="off", password="S3cretPass!", is_active=False)

    response = client.post(reverse("login"), {"username": "off", "password": "S3cretPass!"})

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_logout_clears_session(client, user):
    client.force_login(user)

    response = client.post(reverse("logout"))

    assert response.status_code == 302
    assert "_auth_user_id" not in client.session


def test_idle_timeout_is_configured():
    assert settings.SESSION_COOKIE_AGE > 0
    assert settings.SESSION_SAVE_EVERY_REQUEST is True
