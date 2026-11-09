"""System settings singleton (FR-SET-01, FR-SET-03)."""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class SystemSetting(models.Model):
    class RetentionAction(models.TextChoices):
        ARCHIVE_DELETE = "archive_delete", _("Archive then delete")
        DELETE = "delete", _("Delete")
        KEEP = "keep", _("Keep forever")

    class DisplayMode(models.TextChoices):
        DARK = "dark", _("Dark")
        LIGHT = "light", _("Light")

    class Theme(models.TextChoices):
        LIGHT = "light", _("Light")
        DARK = "dark", _("Dark")
        SYSTEM = "system", _("System")

    retention_jobs_months = models.PositiveSmallIntegerField(
        default=12, validators=[MinValueValidator(1), MaxValueValidator(120)]
    )
    retention_photos_months = models.PositiveSmallIntegerField(
        default=12, validators=[MinValueValidator(1), MaxValueValidator(120)]
    )
    retention_audit_months = models.PositiveSmallIntegerField(
        default=24, validators=[MinValueValidator(1), MaxValueValidator(120)]
    )
    retention_action = models.CharField(
        max_length=20,
        choices=RetentionAction.choices,
        default=RetentionAction.ARCHIVE_DELETE,
    )
    dashboard_refresh_seconds = models.PositiveSmallIntegerField(
        default=15, validators=[MinValueValidator(5), MaxValueValidator(300)]
    )
    display_mode = models.CharField(
        max_length=10, choices=DisplayMode.choices, default=DisplayMode.DARK
    )
    default_language = models.CharField(
        max_length=10,
        choices=[("id", "Bahasa Indonesia"), ("en", "English")],
        default="id",
    )
    default_theme = models.CharField(
        max_length=10, choices=Theme.choices, default=Theme.SYSTEM
    )
    max_photo_kb = models.PositiveIntegerField(
        default=300, validators=[MinValueValidator(50), MaxValueValidator(2048)]
    )
    max_import_mb = models.PositiveSmallIntegerField(
        default=10, validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    idle_timeout_seconds = models.PositiveIntegerField(
        default=43200, validators=[MinValueValidator(300), MaxValueValidator(86400)]
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("system setting")
        verbose_name_plural = _("system settings")

    def __str__(self) -> str:
        return _("System settings")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "SystemSetting":
        """Return the singleton row, creating it with defaults when missing."""
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj
