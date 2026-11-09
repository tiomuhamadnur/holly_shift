"""Health and landing endpoints."""
from django.http import HttpRequest, HttpResponse, JsonResponse


def health(request: HttpRequest) -> JsonResponse:
    """Lightweight liveness probe used by Docker and monitoring."""
    return JsonResponse({"status": "ok"})


def home(request: HttpRequest) -> HttpResponse:
    """Temporary landing page until the design system layout lands in P0."""
    return HttpResponse("Holly Shift - OK")
