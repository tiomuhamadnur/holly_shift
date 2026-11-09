"""User management UI for administrators (P1-T10, P1-T11)."""
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView, FormView, ListView, UpdateView

from .forms import ResetPasswordForm, UserCreateForm, UserForm
from .models import User
from .permissions import PermissionRequiredMixin
from .services import create_user, reset_user_password, update_user


class UserListView(PermissionRequiredMixin, ListView):
    permission_required = "user.view"
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.select_related("role", "personnel").order_by("username")


class UserCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "user.manage"
    model = User
    form_class = UserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("user_list")

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            self.object = create_user(
                username=data["username"],
                password=data["password"],
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                role=data["role"],
                personnel=data["personnel"],
                language=data["language"],
                theme=data["theme"],
                is_active=data["is_active"],
                actor=self.request.user,
                request=self.request,
            )
        except ValidationError as exc:
            form.add_error("password", exc)
            return self.form_invalid(form)
        return HttpResponseRedirect(self.get_success_url())


class UserUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "user.manage"
    model = User
    form_class = UserForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("user_list")

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            self.object = update_user(
                self.object,
                username=data["username"],
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                role=data["role"],
                personnel=data["personnel"],
                language=data["language"],
                theme=data["theme"],
                is_active=data["is_active"],
                actor=self.request.user,
                request=self.request,
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        return HttpResponseRedirect(self.get_success_url())


class UserPasswordResetView(PermissionRequiredMixin, FormView):
    permission_required = "user.manage"
    form_class = ResetPasswordForm
    template_name = "accounts/user_password_reset.html"
    success_url = reverse_lazy("user_list")

    def get_target(self) -> User:
        return get_object_or_404(User, pk=self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.get_target()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["target_user"] = self.get_target()
        return context

    def form_valid(self, form):
        reset_user_password(
            self.get_target(),
            form.cleaned_data["new_password"],
            actor=self.request.user,
            request=self.request,
        )
        messages.success(self.request, _("Temporary password set."))
        return HttpResponseRedirect(self.get_success_url())
