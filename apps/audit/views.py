"""Activity Log viewer: filters, pagination and CSV export (FR-AUD-03)."""
from datetime import date, datetime, time, timedelta

from django.views import View
from django.views.generic import ListView

from apps.accounts.permissions import PermissionRequiredMixin

from .export import audit_csv_response
from .models import JAKARTA, AuditLog


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def filtered_logs(request):
    """Apply the viewer filters; dates are interpreted in Asia/Jakarta (BR-16)."""
    logs = AuditLog.objects.select_related("user").order_by("-at")

    action = request.GET.get("action")
    if action in AuditLog.Action.values:
        logs = logs.filter(action=action)

    entity = request.GET.get("entity")
    if entity:
        logs = logs.filter(entity=entity)

    username = request.GET.get("user")
    if username:
        logs = logs.filter(user__username__icontains=username)

    date_from = _parse_date(request.GET.get("date_from"))
    if date_from:
        logs = logs.filter(
            at__gte=datetime.combine(date_from, time.min, tzinfo=JAKARTA)
        )

    date_to = _parse_date(request.GET.get("date_to"))
    if date_to:
        logs = logs.filter(
            at__lt=datetime.combine(
                date_to + timedelta(days=1), time.min, tzinfo=JAKARTA
            )
        )

    return logs


class AuditLogListView(PermissionRequiredMixin, ListView):
    permission_required = "audit.view"
    template_name = "audit/auditlog_list.html"
    context_object_name = "logs"
    paginate_by = 50

    def get_queryset(self):
        return filtered_logs(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["actions"] = AuditLog.Action.choices
        context["entities"] = (
            AuditLog.objects.values_list("entity", flat=True)
            .distinct()
            .order_by("entity")
        )
        return context


class AuditLogExportView(PermissionRequiredMixin, View):
    permission_required = "audit.view"

    def get(self, request):
        logs = filtered_logs(request).select_related("user")[:10000]
        return audit_csv_response(logs)
