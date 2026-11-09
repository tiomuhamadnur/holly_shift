---
name: excel-import
description: Excel template generation, validation, atomic import, error report and safe export for this project. Use when touching the importer app or any import/export.
---
# Excel import/export

## Principles
- **Standard template only**, downloadable from the system, with `template_version` cell. Users download it first so they never guess the column format.
- **All-or-nothing**: validate the whole file first; if any row fails, reject the entire file and save nothing. Commit inside one `transaction.atomic`.
- Only `.xlsx`. Read with openpyxl `read_only=True, data_only=True` (formulas ignored). Enforce size and row limits from `SystemSetting` (default 5 MB / 5,000 rows).

## Template generation
Sheet `Petunjuk` (how to use, required columns, examples, in the user's language) + data sheet(s) + hidden/visible `template_version`. Required columns marked `*`. Use data validation dropdowns for enums (ORGANIK/TAD, S1/S2/S3/OFF, active). Provide one example row.

## Validation order
1. File type/size -> 2. template version -> 3. sheet and header names -> 4. per-row type/required checks -> 5. referential checks (codes exist and are active) -> 6. uniqueness and duplicates inside the file and against the DB -> 7. domain checks (`week_start` is Monday, `qty` > 0, valid dates, shift exists).
Collect ALL errors (cap at e.g. 500) before reporting.

## Error report
Each error: sheet, row, column, value, reason (translated). Show on screen and offer a downloadable `.xlsx`/`.csv` report. Message must tell the user exactly what to fix.

## Templates (v1)
personnel, shift, equipment, floc, material, tool, template (+ template_material, template_tool), roster, job (+ job_material, job_tool). Column lists are in BRD Appendix A. Multi-value cells use `;`.

## Roster import
`week_start` must be a Monday; values per day are S1/S2/S3/OFF; unknown personnel code rejects the file.

## Job import
`job_ref` links rows across the `job`, `job_material`, `job_tool` sheets; `assignee_codes` separated by `;`.

## History & audit
Create an `ImportBatch` (who, file name, sheet counts, result) and an audit record for every attempt, success or failure.

## Export safety
Prefix cell values starting with `=`, `+`, `-`, `@` with `'` to prevent formula injection. Never export photo payloads.

## Performance
Bulk create with `bulk_create` in chunks; resolve reference codes through dict lookups, not per-row queries.
