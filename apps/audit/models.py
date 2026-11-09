"""Immutable audit trail (FR-AUD-01, FR-AUD-02)."""
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

JAKARTA = ZoneInfo("Asia/Jakarta")


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", _("Create")
        UPDATE = "update", _("Update")
        DELETE = "delete", _("Delete")
        STATUS = "status", _("Status change")
        LOGIN = "login", _("Login")
        LOGOUT = "logout", _("Logout")
        LOGIN_FAILED = "login_failed", _("Login failed")
        IMPORT = "import", _("Import")
        ROLE_CHANGE = "role_change", _("Role change")
        SETTING_CHANGE = "setting_change", _("Setting change")

    at = models.DateTimeField(default=timezone.now, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    action = models.CharField(max_length=30, choices=Action.choices, db_index=True)
    entity = models.CharField(max_length=100, db_index=True)
    entity_id = models.CharField(max_length=128, blank=True)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-at"]
        indexes = [models.Index(fields=["entity", "entity_id"])]

    def __str__(self) -> str:
        return f"{self.at:%Y-%m-%d %H:%M} {self.action} {self.entity}#{self.entity_id}"

    @property
    def at_local(self):
        """Timestamp in Asia/Jakarta for display (BR-16)."""
        return timezone.localtime(self.at, JAKARTA)
