"""Server-side permission enforcement (FR-RBAC, never role-name checks)."""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def _required_codes(value) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def permission_required(*codes: str):
    """Function-view decorator requiring every given permission code."""

    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not all(request.user.has_perm_code(code) for code in codes):
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


class PermissionRequiredMixin:
    """Class-based view mixin requiring every code in ``permission_required``."""

    permission_required: str | tuple[str, ...] = ()

    def get_permission_required(self) -> tuple[str, ...]:
        return _required_codes(self.permission_required)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        codes = self.get_permission_required()
        if codes and not all(request.user.has_perm_code(code) for code in codes):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
