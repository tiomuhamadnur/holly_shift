from django.urls import path

from . import views

urlpatterns = [
    path("", views.AuditLogListView.as_view(), name="auditlog_list"),
    path("export/", views.AuditLogExportView.as_view(), name="auditlog_export"),
]
