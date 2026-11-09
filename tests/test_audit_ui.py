"""Tests for the Activity Log viewer and export (P1-T13)."""
from datetime import UTC, datetime

import pytest
from django.urls import reverse

from apps.accounts.models import Permission, Role, User
from apps.audit.models import AuditLog


@pytest.fixture
def viewer(db):
    permission = Permission.objects.create(code="audit.view", name="View audit")
    role = Role.objects.create(code="auditor", name="Auditor")
    role.permissions.add(permission)
    return User.objects.create_user(username="auditor", password="S3cretPass!", role=role)


@pytest.fixture
def viewer_client(client, viewer):
    client.force_login(viewer)
    return client


def make_log(**kwargs):
    defaults = {"action": AuditLog.Action.CREATE, "entity": "Job", "entity_id": "1"}
    defaults.update(kwargs)
    return AuditLog.objects.create(**defaults)


@pytest.mark.django_db
def test_audit_list_requires_login(client):
    response = client.get(reverse("auditlog_list"))

    assert response.status_code == 302
    assert reverse("login") in response["Location"]


def test_audit_list_denies_without_permission(client, db):
    user = User.objects.create_user(username="plain", password="S3cretPass!")
    client.force_login(user)

    response = client.get(reverse("auditlog_list"))

    assert response.status_code == 403


def test_audit_list_shows_entries(viewer_client):
    make_log(entity="Job", entity_id="7")

    response = viewer_client.get(reverse("auditlog_list"))

    assert response.status_code == 200
    assert b"Job" in response.content
    assert b"7" in response.content


def test_filter_by_action(viewer_client):
    make_log(action=AuditLog.Action.CREATE, entity_id="created")
    make_log(action=AuditLog.Action.DELETE, entity_id="deleted")

    response = viewer_client.get(reverse("auditlog_list"), {"action": "delete"})

    ids = [log.entity_id for log in response.context["logs"]]
    assert "deleted" in ids
    assert "created" not in ids


def test_filter_by_username(viewer_client, viewer):
    other = User.objects.create_user(username="other", password="S3cretPass!")
    make_log(entity_id="keep", user=viewer)
    make_log(entity_id="drop", user=other)

    response = viewer_client.get(reverse("auditlog_list"), {"user": "auditor"})

    ids = [log.entity_id for log in response.context["logs"]]
    assert "keep" in ids
    assert "drop" not in ids


def test_filter_dates_use_jakarta_time(viewer_client):
    make_log(
        entity_id="late-utc",
        at=datetime(2026, 1, 1, 16, 30, tzinfo=UTC),
    )
    make_log(
        entity_id="after-midnight-wib",
        at=datetime(2026, 1, 1, 17, 30, tzinfo=UTC),
    )

    response = viewer_client.get(
        reverse("auditlog_list"), {"date_from": "2026-01-02", "date_to": "2026-01-02"}
    )

    ids = [log.entity_id for log in response.context["logs"]]
    assert ids == ["after-midnight-wib"]


def test_export_neutralises_formulas(viewer_client):
    make_log(entity_id="=cmd()")

    response = viewer_client.get(reverse("auditlog_export"))

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    body = response.content.decode("utf-8")
    assert body.splitlines()[0].startswith("time_wib,user,ip,action")
    assert "'=cmd()" in body


def test_pagination_splits_entries(viewer_client):
    for index in range(51):
        make_log(entity_id=str(index))

    response = viewer_client.get(reverse("auditlog_list"))

    assert response.context["is_paginated"] is True
    assert response.context["page_obj"].paginator.num_pages == 2
    assert len(response.context["logs"]) == 50
