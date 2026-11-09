"""Audit hooks for authentication events (FR-AUD-01).

Auth signals are used deliberately so every login path (custom view and Django
admin) is audited consistently. This is cross-cutting infrastructure, not
business logic.
"""
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

from .models import AuditLog
from .services import record


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    record(
        actor=user,
        action=AuditLog.Action.LOGIN,
        entity="User",
        entity_id=user.pk,
        request=request,
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    record(
        actor=user,
        action=AuditLog.Action.LOGOUT,
        entity="User",
        entity_id=getattr(user, "pk", ""),
        request=request,
    )


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request=None, **kwargs):
    username = str(credentials.get("username", ""))
    record(
        actor=None,
        action=AuditLog.Action.LOGIN_FAILED,
        entity="User",
        entity_id=username,
        after={"username": username},
        request=request,
    )
