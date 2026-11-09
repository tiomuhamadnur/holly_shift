"""Accounts models: custom user, role and permission (FR-AUTH, FR-RBAC)."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Permission(models.Model):
    """A capability referenced by codename in the server-side checks."""

    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)
    module = models.CharField(max_length=50, blank=True)
    is_implemented = models.BooleanField(
        default=True,
        help_text=_("Permissions added ahead of code are shown but have no effect yet."),
    )

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code


class Role(models.Model):
    """A named bundle of permissions. One user has exactly one role."""

    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(
        default=False,
        help_text=_("Seeded roles cannot be deleted."),
    )
    is_super_admin = models.BooleanField(
        default=False,
        help_text=_("Members of this role count toward the Super Admin floor."),
    )
    permissions = models.ManyToManyField(
        Permission, blank=True, related_name="roles"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    """Application user. Login accepts username or email."""

    class Theme(models.TextChoices):
        LIGHT = "light", _("Light")
        DARK = "dark", _("Dark")
        SYSTEM = "system", _("System")

    email = models.EmailField(_("email address"), blank=True)
    role = models.ForeignKey(
        Role,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="users",
    )
    personnel = models.OneToOneField(
        "master.Personnel",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_account",
    )
    language = models.CharField(
        max_length=10, choices=[("id", "Bahasa Indonesia"), ("en", "English")], default="id"
    )
    theme = models.CharField(
        max_length=10, choices=Theme.choices, default=Theme.SYSTEM
    )
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    must_change_password = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=~models.Q(email=""),
                name="unique_nonempty_email",
            )
        ]

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    @property
    def permission_codes(self) -> set[str]:
        if self.role_id is None:
            return set()
        return set(self.role.permissions.values_list("code", flat=True))

    def has_perm_code(self, code: str) -> bool:
        """Return True when the user's role grants the given permission code."""
        if self.is_superuser:
            return True
        return code in self.permission_codes
