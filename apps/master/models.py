"""Master data models. Personnel is introduced early because User links to it."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Personnel(models.Model):
    """A staff member (organic or outsourced/TAD). Full CRUD arrives in P2."""

    class Type(models.TextChoices):
        ORGANIK = "ORGANIK", _("Organik")
        TAD = "TAD", _("TAD")

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.ORGANIK)
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "personnel"

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
