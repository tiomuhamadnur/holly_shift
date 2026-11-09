"""Authentication views. Thin wrappers around Django's built-in auth views."""
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from apps.audit.models import AuditLog
from apps.audit.services import record
from apps.core.images import compress_image

from .forms import EmailOrUsernameAuthenticationForm, ProfileForm
from .models import User

PROFILE_PHOTO_SIDE = 256


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailOrUsernameAuthenticationForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("login")


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        if user.must_change_password:
            user.must_change_password = False
            user.save(update_fields=["must_change_password"])
        return HttpResponseRedirect(self.get_success_url())


class ProfileView(LoginRequiredMixin, UpdateView):
    """Edit the signed-in user's photo, language and theme (P1-T05)."""

    template_name = "accounts/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        original = User.objects.get(pk=self.request.user.pk)
        before = self._snapshot(original)

        upload = self.request.FILES.get("photo")
        if upload:
            compressed = compress_image(upload, max_side=PROFILE_PHOTO_SIDE)
            form.instance.photo.save(
                f"profiles/{form.instance.pk}.jpg", compressed, save=False
            )

        response = super().form_valid(form)
        record(
            self.request.user,
            AuditLog.Action.UPDATE,
            "User",
            form.instance.pk,
            before=before,
            after=self._snapshot(form.instance),
            request=self.request,
        )
        return response

    @staticmethod
    def _snapshot(user: User) -> dict:
        return {
            "language": user.language,
            "theme": user.theme,
            "has_photo": bool(user.photo),
        }
