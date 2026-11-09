"""Settings screen for Super Admins (P1-T14)."""
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import UpdateView

from apps.accounts.permissions import PermissionRequiredMixin

from .forms import SystemSettingForm
from .models import SystemSetting
from .services import update_settings


class SystemSettingView(PermissionRequiredMixin, UpdateView):
    permission_required = "settings.manage"
    form_class = SystemSettingForm
    template_name = "core/settings.html"
    success_url = reverse_lazy("settings")

    def get_object(self, queryset=None):
        return SystemSetting.load()

    def form_valid(self, form):
        self.object = update_settings(
            self.get_object(),
            data=form.cleaned_data,
            actor=self.request.user,
            request=self.request,
        )
        messages.success(self.request, _("Settings saved."))
        return HttpResponseRedirect(self.get_success_url())
