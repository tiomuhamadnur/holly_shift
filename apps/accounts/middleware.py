"""Account middleware: forced password change and per-user language."""
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import translation

from apps.core.services import get_settings

EXEMPT_PREFIXES = ("/admin/", "/static/", "/media/")


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            user is not None
            and user.is_authenticated
            and getattr(user, "must_change_password", False)
        ):
            exempt = {
                reverse("password_change"),
                reverse("login"),
                reverse("logout"),
            }
            if request.path not in exempt and not request.path.startswith(EXEMPT_PREFIXES):
                return redirect(reverse("password_change"))
        return self.get_response(request)


class UserLanguageMiddleware:
    """Activate the signed-in user's saved language (P1-T05)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        settings_obj = get_settings()
        request.system_settings = settings_obj
        if user is not None and user.is_authenticated and getattr(user, "language", None):
            language = user.language
        else:
            language = settings_obj.default_language
        if language:
            translation.activate(language)
            request.LANGUAGE_CODE = language
        return self.get_response(request)
