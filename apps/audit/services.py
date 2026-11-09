"""Audit recording service. Every state change goes through here (skill: audit)."""
from typing import Any

from django.db import transaction

from .models import AuditLog


def client_ip(request) -> str | None:
    """Resolve the caller IP, honouring the reverse proxy header."""
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@transaction.atomic
def record(
    actor,
    action: str,
    entity: str,
    entity_id: Any = "",
    before: Any = None,
    after: Any = None,
    request=None,
) -> AuditLog:
    """Write one immutable audit entry (FR-AUD-01)."""
    user = actor if getattr(actor, "is_authenticated", False) else None
    return AuditLog.objects.create(
        user=user,
        ip=client_ip(request),
        action=action,
        entity=entity,
        entity_id="" if entity_id is None else str(entity_id),
        before=before,
        after=after,
    )
