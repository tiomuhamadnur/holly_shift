---
name: shift-domain-rules
description: Domain rules for shifts, operational day, roster, job status, carry-over, handover and dashboard numbers. Use before touching roster, jobs, scheduler or dashboard logic.
---
# Shift domain rules (summary of BRD section 8; BRD wins on conflict)

## Shifts (from master data, never hardcode)
S1 06:00-15:00, S2 14:00-23:00, S3 22:00-07:00 (spans midnight).
Overlap windows: 06:00-07:00 (S3+S1), 14:00-15:00 (S1+S2), 22:00-23:00 (S2+S3). In overlap two shifts are active; dashboards show both.

## Operational day
Starts at Shift 1 (06:00). Shift 3 belongs to the operational day on which it started.
Example: S3 starting Mon 22:00 ends Tue 07:00 and is operational day **Monday**.
Implement one helper `operational_date(dt)` and one `active_shifts(dt)` in `apps/core/time.py`; everything else uses them. Test boundary minutes: 05:59, 06:00, 06:59, 07:00, 14:00, 15:00, 22:00, 22:59, 23:00, 23:59, 00:00.

## Roster
Weekly (Mon-Sun). One value per personnel per day: S1/S2/S3/OFF. No validation of working hours/rest/competency. No attendance tracking. Manual edit must be easy (swap/replace personnel for one shift in <= 3 clicks). Optimistic lock via `version`.

## Job status machine
Belum -> Sedang | Selesai | Pending* | Batal*
Sedang -> Selesai | Pending* | Batal*
Pending -> Belum (reactivate with date+shift) | Batal*
Selesai -> Sedang (Admin re-open, reason)
Batal -> Belum (Admin re-open, reason)
(*) reason mandatory, photo optional (max 3, compressed base64 in `attachments`).
Admin and Teknisi (field) can change status. Timestamps started_at/finished_at set automatically. No per-job target time; a job belongs to a shift.

## Carry-over (scheduler, idempotent)
At each shift end (S1 15:00, S2 23:00, S3 07:00 Asia/Jakarta): jobs in the ending shift with status Belum or Sedang move to the next shift (S1->S2->S3->S1 of next operational day).
Pending, Batal, Selesai never move.
Each move: carry_count += 1, create JobCarryOver (from/to shift+date, auto note, optional manual note, timestamp), audit log. Running it twice must not move a job twice (guard by from_shift/date).
Jobs with carry_count > 0 get a "Terbawa" badge (delay indicator).
Pending jobs appear in the Pending backlog until reactivated or cancelled.

## Numbers
Persen selesai = Selesai / (all scheduled jobs in scope - Batal). Pending counts in the denominator. Scope = shift, operational day, or range.
Kelengkapan % = checklist items marked Siap / total items.

## Conflicts
Latest write wins, but a stale form warns before overwriting (version check). All changes audited.

## Display privacy
Public display shows minimum data: personnel names, job titles, status. No photos, phone numbers, or detailed reasons.
