"""Login throttling: temporary lockout after repeated failures (FR-AUTH-06)."""
from django.conf import settings
from django.core.cache import cache

KEY_PREFIX = "login_fail"


def _key(identifier: str, ip: str) -> str:
    return f"{KEY_PREFIX}:{identifier.strip().lower()}:{ip}"


def is_locked(identifier: str, ip: str = "") -> bool:
    """Return True when the identifier/IP pair exceeded the failure limit."""
    return cache.get(_key(identifier, ip), 0) >= settings.LOGIN_MAX_ATTEMPTS


def register_failure(identifier: str, ip: str = "") -> int:
    """Record a failed attempt and return the running count for this window."""
    key = _key(identifier, ip)
    try:
        return cache.incr(key)
    except ValueError:
        cache.set(key, 1, settings.LOGIN_LOCKOUT_SECONDS)
        return 1


def reset_failures(identifier: str, ip: str = "") -> None:
    """Clear the failure counter after a successful login."""
    cache.delete(_key(identifier, ip))
