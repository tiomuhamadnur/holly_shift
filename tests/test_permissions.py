"""Tests for permission catalog, seeding and server-side enforcement (P1-T07, P1-T08)."""
import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import HttpResponse
from django.test import RequestFactory
from django.views import View

from apps.accounts.models import Permission, Role, User
from apps.accounts.permissions import PermissionRequiredMixin, permission_required

EXPECTED_PERMISSION_COUNT = 21
EXPECTED_ROLE_CODES = {"super_admin", "admin", "supervisor", "teknisi", "display"}


@pytest.mark.django_db
def test_seed_roles_creates_catalog_and_builtin_roles():
    call_command("seed_roles")

    assert Permission.objects.count() == EXPECTED_PERMISSION_COUNT
    assert set(Role.objects.values_list("code", flat=True)) == EXPECTED_ROLE_CODES
    assert Role.objects.get(code="super_admin").permissions.count() == EXPECTED_PERMISSION_COUNT
    assert set(Role.objects.get(code="display").permissions.values_list("code", flat=True)) == {
        "display.view"
    }


@pytest.mark.django_db
def test_seed_roles_is_idempotent():
    call_command("seed_roles")
    call_command("seed_roles")

    assert Role.objects.count() == len(EXPECTED_ROLE_CODES)
    assert Permission.objects.count() == EXPECTED_PERMISSION_COUNT


@pytest.fixture
def user_with_job_view(db):
    permission = Permission.objects.create(code="job.view", name="View jobs")
    role = Role.objects.create(code="teknisi", name="Teknisi")
    role.permissions.add(permission)
    return User.objects.create_user(username="teknisi1", password="S3cretPass!", role=role)


def test_decorator_allows_user_with_permission(user_with_job_view):
    request = RequestFactory().get("/protected/")
    request.user = user_with_job_view

    @permission_required("job.view")
    def protected(request):
        return HttpResponse("ok")

    response = protected(request)

    assert response.status_code == 200


def test_decorator_redirects_anonymous():
    request = RequestFactory().get("/protected/")
    request.user = AnonymousUser()

    @permission_required("job.view")
    def protected(request):
        return HttpResponse("ok")

    response = protected(request)

    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_decorator_denies_without_permission(user_with_job_view):
    request = RequestFactory().get("/protected/")
    request.user = user_with_job_view

    @permission_required("job.edit")
    def protected(request):
        return HttpResponse("ok")

    with pytest.raises(PermissionDenied):
        protected(request)


class ProtectedView(PermissionRequiredMixin, View):
    permission_required = "job.view"

    def get(self, request):
        return HttpResponse("ok")


def test_mixin_allows_user_with_permission(user_with_job_view):
    request = RequestFactory().get("/protected/")
    request.user = user_with_job_view

    response = ProtectedView.as_view()(request)

    assert response.status_code == 200


def test_mixin_redirects_anonymous():
    request = RequestFactory().get("/protected/")
    request.user = AnonymousUser()

    response = ProtectedView.as_view()(request)

    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_mixin_denies_without_permission(user_with_job_view):
    request = RequestFactory().get("/protected/")
    request.user = user_with_job_view

    class OtherView(PermissionRequiredMixin, View):
        permission_required = "job.edit"

        def get(self, request):
            return HttpResponse("ok")

    with pytest.raises(PermissionDenied):
        OtherView.as_view()(request)
