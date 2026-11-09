# AGENTS.md — Shift Management System (READ FIRST, EVERY SESSION)

## 0. Project in one paragraph
Internal web app (Django + PostgreSQL + HTMX + Tailwind, Docker) for: weekly rosters (3 shifts), daily jobs per shift with material/tools readiness checklists, automatic carry-over of unfinished jobs, a room-display dashboard, realtime supervisor monitoring, Excel mass import, role & permission management, audit log, id/en UI, per-user theme. **Internal network only, no internet at runtime.** Solo developer, vibe-coded with opencode (free models). Go-live target: Q1 2027.

**Source of truth order:** `docs/BRD.md` (WHAT) > `PROGRESS.md` (WHERE WE ARE) > this file (HOW) > code.
If they conflict: STOP and ask the human. Never silently change a requirement.

## 1. SESSION START (mandatory, in this order)
1. Read `PROGRESS.md` lines 1–60 (`CURRENT STATE`) only.
2. Read only the active phase section of `PROGRESS.md`. Never the whole file.
3. `git status -sb` and `git log --oneline -5`.
4. Read only the BRD sections named in the task (e.g. `FR-MD-07`, `BR-03`). Never the whole BRD.
5. Find code with graphify (section 9), not by listing directories.
6. Reply with: task ID, files to touch (max 5), plan (≤5 bullets), tests to write. Continue unless the task is marked `ASK`.

Shortcut: the `/resume` command does steps 1–6.

## 2. SESSION END (mandatory)
1. `make check` must pass (lint + tests + migrations check + i18n check). Never end on red without recording it.
2. Update `PROGRESS.md`: tick the task, rewrite `CURRENT STATE`, append ONE line to `Session Log`.
3. Commit (Conventional Commits). Shortcut: `/wrapup`.
4. If unfinished: write the exact next step, files, and blocker in `CURRENT STATE`.

## 3. Which file to read before doing what
| You are about to… | Read first |
|---|---|
| write models/views/services/migrations/scheduler | `.opencode/skills/django-conventions/SKILL.md` |
| touch templates, CSS, any screen | `.opencode/skills/ui-design-system/SKILL.md` |
| write or fix tests | `.opencode/skills/testing-pytest/SKILL.md` |
| touch Excel import/export | `.opencode/skills/excel-import/SKILL.md` |
| touch shifts, roster, jobs, status, carry-over, dashboard numbers | `.opencode/skills/shift-domain-rules/SKILL.md` |
| start/end session, update progress | `.opencode/skills/session-handoff/SKILL.md` |

Open the skill file explicitly. Do not assume it was auto-loaded.

## 4. Stack & commands
Python 3.12 · Django · PostgreSQL · HTMX · Alpine.js · Tailwind (standalone CLI) + DaisyUI · openpyxl · pytest · ruff · Docker Compose.

| Command | Purpose |
|---|---|
| `make dev` | start dev stack (hot reload) |
| `make test` | pytest with coverage |
| `make check` | ruff + tests + `makemigrations --check` + i18n sync check |
| `make migrate` / `make seed` | migrate / load seed roles, shifts, settings |
| `make css` | build Tailwind |
| `make prod` | production stack (server only) |
| `make backup` | pg_dump with rotation |

Run commands inside containers via `make`; do not install packages on the host.

## 5. DO
- One task per session. Small diffs. Smallest vertical slice: model → service → view → template → test.
- Business logic lives in `apps/<app>/services.py`. Views stay thin, templates dumb.
- Test first for logic and for every bug (reproduce with a failing test, then fix).
- Check permission **codenames** on the server (mixins/decorators), never role names.
- Use `transaction.atomic` for multi-row writes; use `select_related/prefetch_related` on lists.
- Write every state change through the audit service (who, when, before/after).
- Every user-visible string uses gettext (`_()` / `{% trans %}`); update `locale/id` and `locale/en` together.
- Store datetimes timezone-aware (UTC), display Asia/Jakarta. Operational day rules: see domain skill.
- Handle empty, loading, error states on every screen. Mobile-first, accessible.
- Use HTMX partials for dynamic updates; Alpine only for tiny local interactions.
- Make scheduler commands idempotent and log what they did.
- Put settings in env vars / `SystemSetting`; configurable things (retention, refresh interval, display mode) are never hardcoded.
- Pin dependency versions; record every new dependency as a decision in `PROGRESS.md`.
- Soft-deactivate master data; never hard-delete referenced rows.
- Keep functions ≤ 40 lines, type hints on services, docstring on public services.
- Ask the human when requirements are ambiguous. Record the question in `PROGRESS.md` → `Open Items`.

## 6. DON'T
- Don't put business logic in views, templates, or signals.
- Don't use raw SQL with string formatting; don't use `@csrf_exempt`; don't use `mark_safe` on user data.
- Don't set `DEBUG=True` in prod; don't commit `.env`, secrets, dumps, or `graphify-out/cache`.
- **Don't use any external CDN, font, icon, or URL at runtime** (internal network, offline). Self-host everything.
- Don't add React/Vue/SPA, Celery, WebSocket, or any new framework without a recorded human decision. **Redis + SSE are approved (BRD DEC-22)** — use only as specified.
- Don't add a package you have not verified exists (check `pip index versions <pkg>` / official docs). No invented APIs: read the installed source or docs.
- Don't edit already-applied migrations; don't squash without approval.
- Don't delete, skip, or weaken tests to make them pass; don't disable lint rules to silence errors.
- Don't hardcode role names, shift times, strings, thresholds, or the retention period.
- Don't load photo base64 in list queries; photos live in `attachments` (separate table), fetched on demand.
- Don't store auth tokens in localStorage; don't log passwords, tokens, or photo payloads.
- Don't refactor unrelated code; don't rewrite files > 200 lines in one go; don't reformat whole files.
- Don't use bare `except:` / `except Exception: pass`; don't leave `print`/debug code; no TODO without a `PROGRESS.md` entry.
- Don't run destructive commands: `rm -rf` outside tmp, `git reset --hard`, `git push --force`, `DROP`, `docker volume rm`, anything touching `/mnt` or prod data.
- Don't change `docs/BRD.md` unless the human explicitly asks; then log it in the BRD decision table.
- Don't claim "done" without running `make check` and showing its result.

## 7. Architecture rules
- Apps: `accounts`, `master`, `roster`, `jobs`, `importer`, `dashboard`, `audit`, `core`. A module imports another app's **services**, not its views.
- Settings split: `config/settings/{base,dev,prod}.py`. Prod: secure cookies, `ALLOWED_HOSTS` from env, HSTS when HTTPS.
- Scheduler (`docker/scheduler/crontab`) calls management commands: `carry_over`, `apply_retention`, `backup`. Never rely on a user request to trigger them.
- Realtime = Redis Pub/Sub → SSE (HTMX SSE ext) with polling fallback (interval from `SystemSetting`, default 15 s). Publish on every status/roster/carry-over change. Dashboard partial endpoints must be cheap (< 300 ms) and show a stale indicator on failure.
- Optimistic locking: `version` field on Job and RosterEntry; stale form → warn before overwrite.
- Role ↔ Permission is many-to-many; one user = one role; at least one active Super Admin always.

## 8. Security rules
Server-side authorization on every view and HTMX endpoint · CSRF on · password policy + login rate limit · session cookies `Secure`/`HttpOnly`/`SameSite=Lax` in prod · validate file type and size on upload (xlsx, images) · sanitize Excel output against formula injection · least-privilege DB user · run `pip-audit` each phase · review every diff touching `accounts`, `permissions`, `importer` · public/display endpoints: token-based, GET-only, minimal data (BR-15), revocable token, CSP `frame-ancestors` allowlist for the Zabbix embed.

## 9. Token economy (graphify + habits)
- After Phase 0 scaffold: `uv tool install graphifyy` → `graphify install --platform opencode` → `graphify opencode install` → `/graphify .`. Keep it fresh with `graphify hook install` (post-commit). Verify the opencode plugin/AGENTS section actually got installed; if not, rely on the rules below.
- **Query first:** use `graphify query "<question>"` / `graphify explain <node>` to locate code, then open only the needed files with a line range.
- Do not read `graphify-out/GRAPH_REPORT.md` every session (costly). Only for architecture reviews.
- Never paste whole files into chat; use edit tools. Use `view` with ranges, `grep` with narrow patterns.
- Exclude from graph/search: `node_modules`, `staticfiles`, `media`, `.venv`, `locale/*.mo`, `graphify-out/cache`.
- Keep answers short: plan, diff, test result. No long explanations unless asked.
- Context hygiene: after ~30 messages, or when you repeat an error twice, run `/wrapup` and continue in a **new session**.
- Commit `graph.json` if small (< 2 MB); ignore `graphify-out/cache` and `graph.html`.

## 10. Vibe-coding best practices
1. **Plan → diff → test → commit.** Never code before stating the plan.
2. Restate the requirement and acceptance criteria in your own words before coding.
3. Review your own diff for: permissions, i18n, N+1 queries, empty/error states, audit logging.
4. Git is the checkpoint: branch per task `feat/P2-T05-equipment-master`, commit before risky changes, commits small and green.
5. Same error twice → stop, summarize hypotheses, record under `Blockers`, ask the human. No third blind retry.
6. Prefer boring, explicit code over clever code. Reuse existing helpers: search the graph before creating a new one.
7. Verify by running, not by asserting. Show command + result.
8. Specific prompts beat long prompts: file paths + acceptance criteria.
9. When the model changes mid-task, treat it as a new session: run `/resume`, trust `PROGRESS.md`, not chat history.
10. Weak or free model? Make tasks smaller, list exact files, ask for the plan first, and refuse to invent APIs.

## 11. UI/UX (summary; details in `ui-design-system` skill)
Responsive (mobile-first), modern, clean, futuristic: dark-first deep navy surfaces, glass cards, restrained cyan/violet accents, rounded corners, subtle motion (150–200 ms, respects reduced motion), monospace numerals for times/counts, consistent status colors, 44 px touch targets, WCAG AA. Room display: 1920×1080, ≥ 24 px text, no interaction, auto-paging, stale indicator. All assets self-hosted.

## 12. Data & domain invariants (summary; details in `shift-domain-rules` skill)
- Shifts: S1 06–15, S2 14–23, S3 22–07 (from master, not hardcoded). Three overlap windows (06–07, 14–15, 22–23).
- Operational day starts at Shift 1; Shift 3 belongs to the day it started.
- Carry-over at shift end: Belum/Sedang → next shift; Pending/Batal/Selesai stay. Pending/Batal need a reason; photo optional (max 3).
- Persen selesai = Selesai ÷ (all scheduled − Batal).
- Excel import is atomic: any error rejects the whole file with row/column/reason.
- Photos compressed, base64, separate table, never in lists.

## 13. Definition of Done
Code + tests green (`make check`) · permission tested · audit written · i18n id+en complete · empty/error states · responsive checked (360 / 768 / 1280) · no external assets · `PROGRESS.md` updated · committed.

## 14. Git conventions
Branch `feat|fix|chore/<phase>-<task>-<slug>` · Conventional Commits (`feat(jobs): carry-over service`) · never commit to `main` directly after Phase 0 · tag each phase end `phase-N-done`.

## 15. When blocked or unsure
Write the question in `PROGRESS.md` → `Open Items` with a proposed default, tell the human in one short message, and continue with another unblocked task if one exists.
