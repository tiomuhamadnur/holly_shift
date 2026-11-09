"""Account services: password lifecycle and role management."""
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify
from django.utils.translation import gettext as _

from apps.audit.models import AuditLog
from apps.audit.services import record

from .models import Role, User


def set_temporary_password(user, raw_password: str):
    """Validate and set a temporary password, forcing a change on next login.

    Used by admins when resetting another user's password.
    """
    validate_password(raw_password, user=user)
    user.set_password(raw_password)
    user.must_change_password = True
    user.save(update_fields=["password", "must_change_password"])
    return user


def _role_snapshot(role: Role) -> dict:
    return {
        "name": role.name,
        "description": role.description,
        "permissions": sorted(role.permissions.values_list("code", flat=True)),
    }


def _unique_code(name: str) -> str:
    base = slugify(name) or "role"
    code = base
    suffix = 2
    while Role.objects.filter(code=code).exists():
        code = f"{base}-{suffix}"
        suffix += 1
    return code


@transaction.atomic
def create_role(*, name, permissions=(), description="", actor=None, request=None) -> Role:
    """Create a custom role and audit it (FR-RBAC-01, FR-RBAC-06)."""
    role = Role.objects.create(code=_unique_code(name), name=name, description=description)
    role.permissions.set(permissions)
    record(
        actor,
        AuditLog.Action.CREATE,
        "Role",
        role.pk,
        after=_role_snapshot(role),
        request=request,
    )
    return role


@transaction.atomic
def update_role(
    role: Role, *, name, permissions=(), description="", actor=None, request=None
) -> Role:
    """Update a role's name/description/permissions and audit the change."""
    before = _role_snapshot(role)
    role.name = name
    role.description = description
    role.save(update_fields=["name", "description"])
    role.permissions.set(permissions)
    record(
        actor,
        AuditLog.Action.UPDATE,
        "Role",
        role.pk,
        before=before,
        after=_role_snapshot(role),
        request=request,
    )
    return role


@transaction.atomic
def delete_role(role: Role, *, actor=None, request=None) -> None:
    """Delete a custom role; built-in roles are protected (FR-RBAC-04)."""
    if role.is_system:
        raise ValidationError(_("Built-in roles cannot be deleted."))
    before = _role_snapshot(role)
    role_pk = role.pk
    role.delete()
    record(
        actor,
        AuditLog.Action.DELETE,
        "Role",
        role_pk,
        before=before,
        request=request,
    )


def _user_snapshot(user: User) -> dict:
    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role.code if user.role_id else None,
        "personnel": user.personnel_id,
        "language": user.language,
        "theme": user.theme,
        "is_active": user.is_active,
    }


def _is_active_super_admin(user: User) -> bool:
    return bool(user.is_active and user.role_id and user.role.is_super_admin)


def ensure_super_admin_floor(user: User, *, new_role=None, new_active: bool = True) -> None:
    """Raise if the change would leave zero active Super Admins (BR-13)."""
    if not _is_active_super_admin(user):
        return
    will_remain = bool(new_active and new_role is not None and new_role.is_super_admin)
    if will_remain:
        return
    others = User.objects.filter(is_active=True, role__is_super_admin=True).exclude(
        pk=user.pk
    )
    if not others.exists():
        raise ValidationError(_("At least one active Super Admin must remain."))


@transaction.atomic
def create_user(
    *,
    username,
    password,
    email="",
    first_name="",
    last_name="",
    role=None,
    personnel=None,
    language="id",
    theme="system",
    is_active=True,
    actor=None,
    request=None,
) -> User:
    """Create a user with a temporary password and audit it (FR-AUTH-08)."""
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        personnel=personnel,
        language=language,
        theme=theme,
        is_active=is_active,
    )
    validate_password(password, user=user)
    user.set_password(password)
    user.must_change_password = True
    user.save()
    record(
        actor,
        AuditLog.Action.CREATE,
        "User",
        user.pk,
        after=_user_snapshot(user),
        request=request,
    )
    return user


@transaction.atomic
def update_user(
    user: User,
    *,
    username,
    email="",
    first_name="",
    last_name="",
    role=None,
    personnel=None,
    language="id",
    theme="system",
    is_active=True,
    actor=None,
    request=None,
) -> User:
    """Update a user; refuses to remove the last active Super Admin (BR-13)."""
    original = User.objects.get(pk=user.pk)
    ensure_super_admin_floor(original, new_role=role, new_active=is_active)
    before = _user_snapshot(original)
    user.username = username
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.role = role
    user.personnel = personnel
    user.language = language
    user.theme = theme
    user.is_active = is_active
    user.save()
    record(
        actor,
        AuditLog.Action.UPDATE,
        "User",
        user.pk,
        before=before,
        after=_user_snapshot(user),
        request=request,
    )
    return user


@transaction.atomic
def reset_user_password(user: User, raw_password: str, *, actor=None, request=None) -> User:
    """Admin reset: set a temporary password and force a change (FR-AUTH-05)."""
    before = {"must_change_password": user.must_change_password}
    set_temporary_password(user, raw_password)
    record(
        actor,
        AuditLog.Action.UPDATE,
        "User",
        user.pk,
        before=before,
        after={"must_change_password": True, "password_reset": True},
        request=request,
    )
    return user
