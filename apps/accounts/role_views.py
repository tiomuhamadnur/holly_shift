"""Role management UI for Super Admins (P1-T09, FR-RBAC-01..03)."""
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import RoleForm
from .models import Permission, Role
from .permissions import PermissionRequiredMixin
from .services import create_role, delete_role, update_role


def permission_groups() -> dict:
    groups: dict = {}
    for permission in Permission.objects.order_by("module", "code"):
        groups.setdefault(permission.module or "other", []).append(permission)
    return groups


class RoleFormContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["permission_groups"] = permission_groups()
        if self.request.method == "POST":
            context["selected_ids"] = {
                int(value)
                for value in self.request.POST.getlist("permissions")
                if value.isdigit()
            }
        else:
            obj = getattr(self, "object", None)
            context["selected_ids"] = (
                set(obj.permissions.values_list("pk", flat=True)) if obj else set()
            )
        return context


class RoleListView(PermissionRequiredMixin, ListView):
    permission_required = "role.manage"
    model = Role
    template_name = "accounts/role_list.html"
    context_object_name = "roles"

    def get_queryset(self):
        return (
            Role.objects.annotate(permission_count=Count("permissions"))
            .order_by("name")
        )


class RoleCreateView(RoleFormContextMixin, PermissionRequiredMixin, CreateView):
    permission_required = "role.manage"
    model = Role
    form_class = RoleForm
    template_name = "accounts/role_form.html"
    success_url = reverse_lazy("role_list")

    def form_valid(self, form):
        self.object = create_role(
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
            permissions=form.cleaned_data["permissions"],
            actor=self.request.user,
            request=self.request,
        )
        return HttpResponseRedirect(self.get_success_url())


class RoleUpdateView(RoleFormContextMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "role.manage"
    model = Role
    form_class = RoleForm
    template_name = "accounts/role_form.html"
    success_url = reverse_lazy("role_list")

    def form_valid(self, form):
        self.object = update_role(
            self.object,
            name=form.cleaned_data["name"],
            description=form.cleaned_data["description"],
            permissions=form.cleaned_data["permissions"],
            actor=self.request.user,
            request=self.request,
        )
        return HttpResponseRedirect(self.get_success_url())


class RoleDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "role.manage"
    model = Role
    template_name = "accounts/role_confirm_delete.html"
    success_url = reverse_lazy("role_list")

    def form_valid(self, form):
        try:
            delete_role(self.object, actor=self.request.user, request=self.request)
        except ValidationError as exc:
            messages.error(self.request, exc.messages[0])
        except ProtectedError:
            messages.error(
                self.request,
                _("This role is assigned to users and cannot be deleted."),
            )
        return redirect(self.success_url)
