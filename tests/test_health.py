"""Health endpoint smoke test (FR-OPS-03)."""
import pytest


@pytest.mark.django_db
def test_health_returns_ok(client):
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_home_returns_ok(client):
    response = client.get("/")

    assert response.status_code == 200
