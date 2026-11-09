# Security Checklist — Phase 1

Scope: authentication, roles/permissions, audit, settings, uploads.
Status as of 2026-11-09. Re-run each phase (AGENTS §8).

## Authentication & sessions

- [x] Login by username **or** email, case-insensitive (`apps/accounts/backends.py`)
- [x] Inactive users rejected (`ModelBackend.user_can_authenticate`)
- [x] Password validators: similarity, min length 8, common, numeric (`config/settings/base.py`)
- [x] Forced password change on first login / admin reset (`apps/accounts/middleware.py`, `services.set_temporary_password`)
- [x] Login lockout after 5 failures per username+IP (`apps/accounts/throttle.py`)
- [x] Idle timeout from `SystemSetting` (`apps/core/middleware.py`)
- [x] Session cookie age configured; `SESSION_SAVE_EVERY_REQUEST`
- [ ] Prod cookie flags (`Secure`, `HttpOnly`, `SameSite=Lax`) — verify in `config/settings/prod.py` when Docker/HTTPS available

## Authorization

- [x] Server-side checks by permission **codename**, never role name (`apps/accounts/permissions.py`)
- [x] Superuser bypass for bootstrap only; role permissions seeded (`apps/accounts/catalog.py`)
- [x] Every management view/HTMX endpoint wrapped with `PermissionRequiredMixin` / decorator
- [x] One role per user; role-permission M2M (`apps/accounts/models.py`)
- [x] Last active Super Admin cannot be deactivated or moved (`services.ensure_super_admin_floor`)
- [x] Built-in roles cannot be deleted (`services.delete_role`)

## CSRF & input handling

- [x] CSRF middleware enabled; all POST forms include `{% csrf_token %}`
- [x] No `@csrf_exempt` in codebase
- [x] Uploads: JPEG/PNG/WebP only, size limit from `SystemSetting.max_photo_kb`, server-side re-encode (`apps/core/images.py`)
- [x] Uploaded file names not trusted; stored under generated `profiles/<pk>.jpg`
- [ ] Formula-injection guard on Excel **import/export** (importer app) — P2
- [x] CSV export neutralises `= + - @` prefixes (`apps/audit/export.py`)

## Audit & data protection

- [x] Mutating actions write audit entries with before/after and IP (`apps/audit/services.py`)
- [x] Audit log read-only in admin and UI; no delete/edit path (`apps/audit/admin.py`)
- [x] Passwords, tokens and photo payloads never written to audit
- [x] Secrets from env; `.env` git-ignored; no secrets in code
- [ ] Photo base64 in separate `attachments` table and excluded from list queries — P3

## Transport & deployment (pending tooling)

- [ ] `DEBUG=False` and `ALLOWED_HOSTS` from env in prod
- [ ] HSTS + secure cookies when HTTPS is enabled
- [ ] Least-privilege database user
- [ ] CSP `frame-ancestors` allowlist for Zabbix embed
- [ ] Display token: GET-only, minimal data, revocable (BR-15)

## Dependencies

- [x] Versions pinned in `requirements/*.txt`
- [x] `pip-audit -r requirements/dev.txt` → no known vulnerabilities (2026-11-09)
- [ ] Re-run `pip-audit` each phase and after dependency changes
