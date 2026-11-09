---
name: testing-pytest
description: Testing standards - pytest-django, factories, mandatory coverage areas, edge cases and Definition of Done. Use when writing or fixing tests.
---
# Testing standards

## Tools
pytest, pytest-django, factory_boy, coverage. Run with `make test`; `make check` runs everything. Tests live in `tests/<app>/` mirroring `apps/`.

## Rules
- Every feature ships with tests. A bug fix starts with a failing test.
- Never delete, skip or weaken a test to get green. If a test is wrong, explain why and fix the test in a separate, visible change.
- Prefer testing services directly; add a few view tests for permission and HTMX responses.
- Use factories, not fixtures with hardcoded ids. Freeze time with `freezegun` (or equivalent) for shift/carry-over tests.
- Tests must not need internet.

## Mandatory coverage areas
1. Auth: login by email AND username, wrong password, lockout after 5 failures, forced password change, inactive user.
2. Permissions: every permission codename allows/denies correctly on both full pages and HTMX partials; role edit applies on next request; at least one Super Admin always remains.
3. Role-permission many-to-many behaviour; user has exactly one role.
4. Import: each validation error type, atomic rejection (nothing saved when one row is bad), template version mismatch, oversize file, formula injection on export, translated error report.
5. Time helpers: `operational_date`, `active_shifts` on all boundary minutes (05:59, 06:00, 06:59, 07:00, 14:00, 15:00, 22:00, 22:59, 23:00, 23:59, 00:00).
6. Carry-over: S1->S2, S2->S3, S3->S1 next operational day; midnight crossing; only Belum/Sedang move; Pending/Batal/Selesai stay; idempotent double run; carry_count; handover note; audit entry.
7. Status machine: every allowed and forbidden transition; reason mandatory for Pending/Batal; optional photo; re-open rules.
8. Persen selesai and kelengkapan % with Batal and Pending in the mix; empty scope (no division by zero).
9. Photo compression: size limit, dimension limit, base64 stored in attachments only, not loaded by list queries.
10. Audit: every mutating action produces a record with before/after.
11. Retention command: archive/delete/keep modes, respects settings.
12. i18n: no missing keys between id and en.

## Integration tests (few, valuable)
Import roster -> create job -> change status -> dashboard aggregates change.

## Coverage targets
accounts/audit >= 85%, master/importer >= 85%, jobs >= 90%, overall >= 80%.

## Definition of Done (tests part)
`make check` green, new logic covered, no skipped tests added, edge cases listed above touched by the task are covered.
