"""Authentication, profile and management forms."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from apps.core.services import get_settings
from apps.master.models import Personnel

from .models import Permission, Role

User = get_user_model()


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Email or username"),
        widget=forms.TextInput(
            attrs={"autofocus": True, "autocomplete": "username", "autocapitalize": "none"}
        ),
    )


class ProfileForm(forms.ModelForm):
    """Let a user edit their photo, language and theme (FR-AUTH-07)."""

    class Meta:
        model = User
        fields = ["photo", "language", "theme"]
        widgets = {
            "photo": forms.ClearableFileInput(
                attrs={"accept": "image/jpeg,image/png,image/webp"}
            ),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        limit_kb = get_settings().max_photo_kb
        if photo and getattr(photo, "size", 0) > limit_kb * 1024:
            raise forms.ValidationError(
                _("Image must be %(kb)s KB or smaller.") % {"kb": limit_kb}
            )
        return photo


class RoleForm(forms.ModelForm):
    """Role name, description and permission assignment (FR-RBAC-02)."""

    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.order_by("module", "code"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Role
        fields = ["name", "description", "permissions"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class UserForm(forms.ModelForm):
    """Create/edit a user account; one role per user (FR-AUTH-08)."""

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "personnel",
            "language",
            "theme",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].queryset = Role.objects.order_by("name")
        self.fields["personnel"].queryset = Personnel.objects.order_by("name")


class UserCreateForm(UserForm):
    password = forms.CharField(
        label=_("Temporary password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=_("The user must change it after signing in."),
    )


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label=_("New temporary password"),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password(self):
        value = self.cleaned_data["new_password"]
        validate_password(value, user=self.user)
        return value

