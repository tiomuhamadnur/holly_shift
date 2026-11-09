"""Tests for login throttling / temporary lockout (P1-T04)."""
import pytest
from django.core.cache import cache
from django.urls import reverse

from apps.accounts.models import User
from apps.accounts.throttle import is_locked, register_failure, reset_failures


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="budi", password="S3cretPass!")


def test_register_failure_counts_up():
    assert register_failure("budi", "127.0.0.1") == 1
    assert register_failure("budi", "127.0.0.1") == 2


def test_reset_failures_clears_counter():
    register_failure("budi", "127.0.0.1")
    reset_failures("budi", "127.0.0.1")

    assert is_locked("budi", "127.0.0.1") is False


def test_five_failures_lock_the_identifier(client, user):
    for _ in range(5):
        client.post(reverse("login"), {"username": "budi", "password": "wrong"})

    response = client.post(
        reverse("login"), {"username": "budi", "password": "S3cretPass!"}
    )

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session
    assert is_locked("budi", "127.0.0.1") is True


def test_successful_login_resets_counter(client, user):
    client.post(reverse("login"), {"username": "budi", "password": "wrong"})
    client.post(reverse("login"), {"username": "budi", "password": "wrong"})

    response = client.post(
        reverse("login"), {"username": "budi", "password": "S3cretPass!"}
    )

    assert response.status_code == 302
    assert is_locked("budi", "127.0.0.1") is False


def test_lockout_is_per_ip(client, user):
    for _ in range(5):
        register_failure("budi", "10.0.0.1")

    assert is_locked("budi", "10.0.0.1") is True
    assert is_locked("budi", "10.0.0.2") is False
