"""CSV export helpers with formula-injection protection (FR-AUD-03)."""
import csv
import json
from datetime import date

from django.http import HttpResponse

FORMULA_PREFIXES = ("=", "+", "-", "@")


def safe_cell(value) -> str:
    """Neutralise spreadsheet formula injection in exported text."""
    text = "" if value is None else str(value)
    if text.startswith(FORMULA_PREFIXES):
        return "'" + text
    return text


def audit_csv_response(logs) -> HttpResponse:
    today = date.today()
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="audit-log-{today:%Y%m%d}.csv"'
    )
    writer = csv.writer(response)
    writer.writerow(
        ["time_wib", "user", "ip", "action", "entity", "entity_id", "before", "after"]
    )
    for log in logs:
        writer.writerow(
            [
                log.at_local.strftime("%Y-%m-%d %H:%M:%S"),
                safe_cell(log.user.username if log.user_id else ""),
                safe_cell(log.ip),
                safe_cell(log.action),
                safe_cell(log.entity),
                safe_cell(log.entity_id),
                safe_cell(json.dumps(log.before, ensure_ascii=False) if log.before else ""),
                safe_cell(json.dumps(log.after, ensure_ascii=False) if log.after else ""),
            ]
        )
    return response
