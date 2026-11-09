"""Core middleware: enforce the configured idle timeout (FR-SET-03)."""
from .services import get_settings


class IdleTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(request, "user", None) is not None and request.user.is_authenticated:
            settings_obj = getattr(request, "system_settings", None) or get_settings()
            request.session.set_expiry(settings_obj.idle_timeout_seconds)
        return self.get_response(request)
