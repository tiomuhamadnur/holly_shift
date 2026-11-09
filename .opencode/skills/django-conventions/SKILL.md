---
name: django-conventions
description: Django conventions for this project - layering, models, queries, permissions, audit, i18n, migrations, scheduler commands, settings. Use before writing backend code.
---
# Django conventions

## Layering
`models.py` (data + invariants) -> `services.py` (all business logic, transactional) -> `views.py` (thin: parse, authorize, call service, render) -> `templates/` (dumb). Cross-app calls go through the other app's services only.

## Models
- `created_at`, `updated_at`; `version = PositiveIntegerField(default=1)` on Job and RosterEntry (optimistic lock: compare on save, increment).
- `is_active` for master data; unique `code`; never hard-delete referenced rows (`on_delete=PROTECT`).
- Photos only in `Attachment` (own table). Never `select` the payload in list queries: use `.defer("payload_b64")` or a separate query.
- Datetimes are timezone-aware (UTC in DB). `TIME_ZONE = "Asia/Jakarta"`, `USE_TZ = True`.

## Queries
`select_related` for FKs, `prefetch_related` for reverse/M2M. No queries inside template loops. Add DB indexes for (work_date, shift, status) and roster (personnel, date).

## Permissions
Role <-> Permission many-to-many; one user = one role. Check **permission codenames** (`job.status_update`, ...) via mixin `PermissionRequiredMixin`-style helpers in `apps/accounts/permissions.py`. Never compare role names. HTMX endpoints are protected exactly like full pages. Permissions are re-read per request (no stale cache across role edits).

## Audit
Every create/update/delete/status change/import/role change/setting change calls `audit.services.record(actor, action, entity, before, after, request)`. Never skip it for "small" changes.

## i18n
`gettext`/`gettext_lazy` for every user-visible string including form errors, messages, Excel instructions and error reports. Keep `locale/id` and `locale/en` in sync; `make check` fails otherwise. Language comes from the user's setting, falling back to the system default.

## Forms & validation
Validate on the server always. Use Django forms. Clear, translated messages with field names.

## Transactions
`transaction.atomic` around multi-row writes (import commit, carry-over batch, roster bulk fill). Carry-over must be idempotent.

## Management commands
`carry_over`, `apply_retention`, `backup`, `seed`. Idempotent, log counts, exit non-zero on failure, accept `--dry-run`.

## Settings
`config/settings/base.py` shared; `dev.py` DEBUG on; `prod.py` secure cookies, `ALLOWED_HOSTS` from env, HSTS if HTTPS. Secrets from env only. Runtime-configurable values (retention, refresh interval, display mode, limits) live in `SystemSetting`, read through one cached accessor.

## Migrations
Never edit applied migrations. `makemigrations --check` in `make check`. Data migrations are reversible when possible.

## Style
ruff (lint + format), type hints on services, functions <= 40 lines, docstring on public services, no wildcard imports.
