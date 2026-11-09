# PROGRESS.md — Sumber kebenaran progres proyek

> **AI agent:** baca HANYA baris 1–60 (`CURRENT STATE`) dan section phase yang aktif. Perbarui file ini di akhir setiap sesi (`/wrapup`).
> Ukuran task: **S** ≤ 1 jam · **M** ≤ 3 jam · **L** ≤ 1 hari (L harus dipecah sebelum dikerjakan model gratis). `ASK` = tanya manusia dulu.

---

## CURRENT STATE (tulis ulang setiap sesi)

| | |
|---|---|
| Terakhir diperbarui | 9 Nov 2026 |
| Phase aktif | **P2 — Master Data** (Phase 1 selesai, tag `phase-1-done`) |
| Task aktif | P2-T01 (belum mulai — baca BRD §7 di sesi baru) |
| Selesai terakhir | Phase 1 lengkap: P1-T01..T16 + P0-T07/T10 |
| Langkah berikutnya | Mulai P2-T01 master data sesuai BRD §7 |
| Blocker | OI-06 (model gratis opencode); Docker daemon off → dev sementara pakai venv + SQLite |
| Model AI aktif | big-pickle (opencode) |
| Branch | `main` (repo di-init, tag `phase-1-done`) |
| `make check` terakhir | ruff ✅ · pytest 96 ✅ · makemigrations --check ✅ · i18n check ✅ · coverage 95% · pip-audit bersih (make belum bisa dijalankan — OI-17) |
| Kesehatan timeline | Hijau: Phase 1 selesai. Kuning: P0 sisa Docker/design system/ekstraksi i18n |

---

## Timeline baseline (PO boleh mengubah kapan saja → catat di Timeline Change Log)

| Phase | Isi | Mulai | Selesai | Status |
|---|---|---|---|---|
| P0 | Fondasi, Docker, tooling, design system, graphify | 9 Nov 2026 | 22 Nov 2026 | ☐ |
| P1 | Akun, role & permission, audit, pengaturan | 23 Nov 2026 | 13 Des 2026 | ☐ |
| P2 | Master data + framework import Excel | 14 Des 2026 | 10 Jan 2027 | ☐ |
| P3 | Roster | 11 Jan 2027 | 31 Jan 2027 | ☐ |
| P4 | Pekerjaan, carry-over, serah terima | 1 Feb 2027 | 21 Feb 2027 | ☐ |
| P5 | Dashboard layar & atasan | 22 Feb 2027 | 7 Mar 2027 | ☐ |
| P6 | Hardening, deploy, UAT, go-live | 8 Mar 2027 | 31 Mar 2027 | ☐ |

Titik risiko jadwal: P2 (libur akhir tahun) dan P4 (carry-over penuh edge case). Tidak ada buffer untuk fase 2; bila meleset, geser tanggal secara sadar dan catat.

---

## Phase 0 — Fondasi & Tooling (9–22 Nov 2026)
Tujuan: repo, Docker dev/prod, tooling kualitas, design system dasar, opencode & graphify siap.

- [ ] P0-T01 · S · Init git repo, `.gitignore`, `README.md`, salin kit (AGENTS, PROGRESS, opencode.json, .opencode, docs/BRD.md) · AC: commit awal, struktur sesuai BRD §13
- [ ] P0-T02 · S · Setup opencode: jalankan, pilih model gratis, catat model & limit di CURRENT STATE · AC: opencode membaca AGENTS.md; `/resume` berfungsi · Ref: OI-06
- [x] P0-T03 · M · Scaffold Django: `config/settings/{base,dev,prod}`, apps kosong (accounts, master, roster, jobs, importer, dashboard, audit, core) · AC: `runserver` jalan, halaman health `200` (dibangun pakai venv + SQLite karena Docker daemon off)
- [ ] P0-T04 · M · `docker/Dockerfile` multi-stage (target `dev`, `prod`), `entrypoint.sh` (tunggu DB, migrate, collectstatic) · AC: image dev & prod ter-build
- [ ] P0-T05 · M · `docker-compose.yml` + `docker-compose.dev.yml` (hot reload, Postgres, port DB lokal) · AC: `make dev` menampilkan halaman awal
- [ ] P0-T06 · M · `docker-compose.prod.yml` (gunicorn, nginx, scheduler, restart always, volume DB) + `.env.*.example` · AC: stack prod naik di mesin lokal
- [x] P0-T07 · M · pytest, pytest-django, coverage, factory_boy, ruff, pre-commit, `Makefile` (`dev test check migrate seed css prod backup`) · AC: `make check` hijau (Makefile ditulis; eksekusi menunggu Docker/make — OI-17; pre-commit belum)
- [ ] P0-T08 · M · Tailwind standalone CLI + DaisyUI + font Inter/JetBrains Mono + ikon Lucide **self-hosted**; base layout · AC: tanpa request eksternal (cek tab Network)
- [ ] P0-T09 · M · Design tokens (terang/gelap), komponen dasar: button, card, input, table, badge status, modal, toast, empty state · AC: halaman katalog komponen di `/dev/ui` · Ref: BRD §12
- [x] P0-T10 · S · i18n: locale id/en, language switch skeleton, skrip cek sinkron `.po` di `make check` · Ref: FR-I18N-01 (command `check_i18n` + skeleton `.po`; ekstraksi/terjemahan menunggu gettext — OI-17)
- [x] P0-T11 · S · Health endpoint + logging terstruktur · Ref: FR-OPS-03
- [ ] P0-T12 · M · Install graphify (`uv tool install graphifyy`, `graphify install --platform opencode`, `graphify opencode install`, `/graphify .`, `graphify hook install`) · AC: query graf berhasil; catat apakah plugin/AGENTS section terpasang
- [ ] P0-T13 · S · Verifikasi alur sesi: `/resume` → task kecil → `/wrapup` dengan model gratis · AC: PROGRESS terisi benar
- [ ] P0-T14 · S · Tag `phase-0-done`

## Phase 1 — Akun, Role & Permission, Audit, Pengaturan (23 Nov–13 Des 2026)
Tujuan: fondasi keamanan dan akuntabilitas sebelum fitur bisnis.

- [x] P1-T01 · M · Custom User (email unik opsional, username unik, tautan Personel opsional, language, theme, photo) · Ref: FR-AUTH-02, -07, -09 (model + constraint email unik non-kosong + `has_perm_code`; 6 tes)
- [x] P1-T02 · M · Auth backend login **email atau username** + logout + idle timeout dari setting · Ref: FR-AUTH-01, -03 (backend case-insensitive, LoginView/LogoutView, 8 tes; idle timeout via env sampai P1-T14)
- [x] P1-T03 · M · Kebijakan password, ubah password, wajib ganti saat login pertama, reset oleh admin · Ref: FR-AUTH-04, -05 (validators, PasswordChangeView, middleware wajib-ganti, service `set_temporary_password`; 10 tes)
- [x] P1-T04 · S · Rate limit / lockout 5 gagal · Ref: FR-AUTH-06 (cache-based, per username+IP, `LOGIN_MAX_ATTEMPTS`/`LOGIN_LOCKOUT_SECONDS`; 5 tes)
- [x] P1-T05 · M · Halaman profil: foto (kompres server-side 256 px), bahasa, tema (tersimpan per user, berlaku langsung) · Ref: FR-AUTH-07, FR-I18N-02 (ProfileView + form, middleware bahasa, audit; 7 tes)
- [x] P1-T06 · M · Layanan kompresi gambar (resize, kualitas, base64, batas ukuran) + tes · Ref: BR-14 (`apps/core/images.py`: JPEG, max side/bytes, validasi format; 4 tes)
- [x] P1-T07 · M · Model Role & Permission (many-to-many), katalog permission awal, `make seed` role bawaan · Ref: BRD §6 (21 permission, 5 role, command `seed_roles` idempoten)
- [x] P1-T08 · M · Mixin/dekorator permission server-side + tes akses per role · Ref: FR-RBAC (mixin + decorator, 6 tes)
- [x] P1-T09 · L→pecah · UI kelola Role (CRUD) + matriks assign permission · Ref: FR-RBAC-01..03 (list/create/edit/delete, checkbox per modul, guard role sistem & role terpakai, audit; 9 tes)
- [x] P1-T10 · M · UI kelola User (CRUD, satu role, aktif/nonaktif, reset password) · Ref: FR-AUTH-08 (list/create/edit + reset; tanpa hard-delete; audit; 12 tes)
- [x] P1-T11 · S · Aturan: minimal satu Super Admin aktif; role bawaan tidak bisa dihapus · Ref: FR-RBAC-04 (flag `Role.is_super_admin`, guard di update user + guard hapus role)
- [x] P1-T12 · M · Audit app: model AuditLog, service pencatatan (before/after, IP), integrasi login/logout/gagal · Ref: FR-AUD-01, -02 (model + `record()` + signal auth, admin read-only; 5 tes)
- [x] P1-T13 · M · UI Activity Log (filter, paginasi, ekspor) · Ref: FR-AUD-03 (filter aksi/entitas/user/tanggal WIB, 50/halaman, ekspor CSV anti formula-injection; 8 tes)
- [x] P1-T14 · M · `SystemSetting` + UI pengaturan Super Admin (retensi, refresh, mode layar, bahasa default, batas) · Ref: FR-SET-01, -03 (singleton + form + audit SETTING_CHANGE, middleware idle timeout & bahasa default, `seed_settings`; 8 tes)
- [x] P1-T15 · M · Tes lengkap fase 1 + checklist keamanan + `pip-audit` · AC: coverage `accounts` & `audit` ≥ 85% (coverage total 95% ✅, accounts/audit >85% ✅, pip-audit bersih ✅, checklist `docs/security-checklist.md` ✅)
- [x] P1-T16 · S · Tag `phase-1-done` (commit awal + tag anotasi)

## Phase 2 — Master Data + Framework Import Excel (14 Des 2026–10 Jan 2027)
Tujuan: semua master tersedia dan bisa diimpor sebelum roster/pekerjaan.

- [ ] P2-T01 · M · Komponen daftar generik (cari, filter, paginasi, nonaktifkan) dipakai semua master
- [ ] P2-T02 · M · Personel (Organik/TAD) CRUD · Ref: FR-MD-01
- [ ] P2-T03 · S · Shift master + seed S1/S2/S3 · Ref: FR-MD-02, BR-02
- [ ] P2-T04 · M · Functional Location (parent opsional) · Ref: FR-MD-04, OI-09
- [ ] P2-T05 · M · Equipment (floc default opsional) · Ref: FR-MD-03
- [ ] P2-T06 · S · Material master · Ref: FR-MD-05
- [ ] P2-T07 · S · Tools master · Ref: FR-MD-06
- [ ] P2-T08 · M · Template Pekerjaan + daftar material & tools default (qty) · Ref: FR-MD-07
- [ ] P2-T09 · S · Aturan nonaktif vs hapus, kode unik, tampil di data lama · Ref: BR-12
- [ ] P2-T10 · L→pecah · Framework import: generator template baku (petunjuk, dropdown, versi), parser openpyxl, validasi, commit atomik · Ref: FR-IMP-01, -03
- [ ] P2-T11 · M · Laporan error (sheet/baris/kolom/nilai/alasan, i18n, unduh) · Ref: FR-IMP-04
- [ ] P2-T12 · S · Batas ukuran/baris, hanya xlsx, sanitasi formula injection · Ref: FR-IMP-05, -06
- [ ] P2-T13 · S · Riwayat import (ImportBatch) + audit · Ref: FR-IMP-07
- [ ] P2-T14 · M · Import untuk 6 master + template pekerjaan (3 sheet) · Ref: FR-IMP-02
- [ ] P2-T15 · S · Ekspor Excel master · Ref: FR-MD-08
- [ ] P2-T16 · M · Tes fase 2 (termasuk semua jenis error import) · AC: coverage `master` & `importer` ≥ 85%
- [ ] P2-T17 · S · Ukur baseline waktu penyusunan roster/jadwal saat ini (tanya PO) · Ref: OI-01, G1 · **ASK**
- [ ] P2-T18 · S · Tag `phase-2-done`

## Phase 3 — Roster (11–31 Jan 2027)
- [ ] P3-T01 · M · Model RosterEntry (unik personel+tanggal, S1/S2/S3/OFF, version) · Ref: FR-RO-01, BR-11
- [ ] P3-T02 · L→pecah · Grid mingguan responsif (personel × 7 hari), edit sel 1–2 klik · Ref: FR-RO-02
- [ ] P3-T03 · M · Isi massal (rentang hari / banyak personel) · Ref: FR-RO-02
- [ ] P3-T04 · S · Salin minggu sebelumnya · Ref: FR-RO-03
- [ ] P3-T05 · M · Tampilan per shift: tambah/hapus/ganti personel cepat · Ref: FR-RO-04
- [ ] P3-T06 · M · Import & ekspor Excel roster (template v1, `week_start` Senin) · Ref: FR-RO-05
- [ ] P3-T07 · S · "Jadwal Saya" untuk personel · Ref: FR-RO-06
- [ ] P3-T08 · S · Optimistic lock + peringatan formulir basi · Ref: BR-09
- [ ] P3-T09 · S · Audit perubahan roster (dari→ke) · Ref: FR-RO-07
- [ ] P3-T10 · M · Tes fase 3 + uji mobile 360 px
- [ ] P3-T11 · S · Tag `phase-3-done`

## Phase 4 — Pekerjaan, Carry-over, Serah Terima (1–21 Feb 2027)
- [ ] P4-T01 · M · Model Job (+ number generator `JOB-YYYYMMDD-NNN`, version, carry_count) · Ref: FR-JOB-09
- [ ] P4-T02 · M · JobAssignee, JobMaterial, JobTool (checklist) · Ref: FR-JOB-02
- [ ] P4-T03 · L→pecah · Form buat/ubah pekerjaan (prefill dari template, personel dari roster, peringatan di luar roster) · Ref: FR-JOB-01, BR-10
- [ ] P4-T04 · M · Tampilan perencanaan mingguan + harian per shift · Ref: FR-JOB-03
- [ ] P4-T05 · M · Mesin status (diagram BRD §7.3) + izin + timestamp otomatis · Ref: BR-05, BR-08
- [ ] P4-T06 · M · Alasan wajib Pending/Batal + riwayat status (JobStatusEvent) · Ref: FR-JOB-05
- [ ] P4-T07 · M · Lampiran foto opsional (maks 3, kompres, base64, tabel terpisah, muat on-demand) · Ref: BR-14
- [ ] P4-T08 · S · Toggle checklist Siap/Belum (permission `job.checklist_update`) · Ref: FR-JOB-02
- [ ] P4-T09 · L→pecah · Layanan carry-over (hari operasional, 3 overlap, S3 lintas tengah malam) + management command idempoten · Ref: BR-01..04
- [ ] P4-T10 · S · Catatan serah terima otomatis + manual (opsional) · Ref: BR-04, OI-10
- [ ] P4-T11 · M · Backlog Pending + reaktivasi (tanggal & shift) · Ref: FR-JOB-08
- [ ] P4-T12 · M · Filter & pencarian pekerjaan · Ref: FR-JOB-10
- [ ] P4-T13 · M · Import Excel pekerjaan (3 sheet, referensi `job_ref`) · Ref: FR-JOB-11
- [ ] P4-T14 · S · Re-open Selesai/Batal oleh Admin (alasan wajib) · Ref: BR-05
- [ ] P4-T15 · M · Scheduler container + crontab carry-over (15:00, 23:00, 07:00 WIB) · Ref: FR-OPS-02
- [ ] P4-T16 · L→pecah · Tes edge case carry-over, status, persen selesai · AC: coverage `jobs` ≥ 90%
- [ ] P4-T17 · S · Tag `phase-4-done`

## Phase 5 — Dashboard Layar & Atasan (22 Feb–7 Mar 2027)
- [ ] P5-T01 · M · Layanan agregasi dashboard (shift aktif, personel, jumlah per status, persen selesai, Terbawa, kelengkapan) · Ref: BR-07
- [ ] P5-T02 · L→pecah · Layar ruangan 1920×1080 (tipografi besar, kontras tinggi, dark) · Ref: FR-DB-01
- [ ] P5-T03 · M · Polling HTMX + indikator "terakhir diperbarui" + peringatan basi · Ref: FR-DB-02
- [ ] P5-T04 · S · Paging otomatis bila meluber · Ref: FR-DB-03
- [ ] P5-T05 · M · Mode layar publik/login + token URL + data minimum · Ref: FR-DB-04, BR-15
- [ ] P5-T06 · L→pecah · Dashboard atasan (KPI, filter tanggal/shift, responsif HP) · Ref: FR-DB-05
- [ ] P5-T07 · S · Drill-down ke detail pekerjaan · Ref: FR-DB-06
- [ ] P5-T08 · M · Optimasi query & uji beban ±50 pengguna · Ref: NFR-01
- [ ] P5-T09 · S · Tes dashboard + tag `phase-5-done`

## Phase 6 — Hardening, Deploy, UAT, Go-Live (8–31 Mar 2027)
- [ ] P6-T01 · M · Checklist keamanan penuh + `pip-audit` + review `accounts/importer` · Ref: NFR-03
- [ ] P6-T02 · M · Retensi: command `apply_retention` (arsip terkompresi / hapus / simpan) dari pengaturan · Ref: FR-SET-01, -02
- [ ] P6-T03 · M · `backup.sh`/`restore.sh`, cron harian, rotasi, **uji restore** · Ref: FR-OPS-01
- [ ] P6-T04 · M · Deploy prod: IP statis, subdomain lokal, HTTPS internal (OI-02), nginx · **ASK**
- [ ] P6-T05 · S · Mini PC kiosk (Chromium kiosk, auto-start, auto-reload) · Ref: FR-DB-07
- [ ] P6-T06 · M · Seed data nyata via template Excel (master, roster minggu pertama)
- [ ] P6-T07 · L→pecah · UAT 15 skenario (BRD §18) bersama pengguna; catat temuan
- [ ] P6-T08 · M · Perbaikan temuan UAT
- [ ] P6-T09 · M · Panduan pengguna singkat id/en + panduan admin + runbook (restart, restore, ganti sertifikat)
- [ ] P6-T10 · S · Rencana rollback + checklist go-live · **ASK**
- [ ] P6-T11 · S · Go-live + tag `v1.0.0`
- [ ] P6-T12 · M · Hypercare 2 minggu (pasca go-live) · Ref: OI-12

---

## Timeline Change Log (PO mengubah timeline di sini)
| Tanggal | Perubahan | Alasan | Oleh |
|---|---|---|---|
| 9 Nov 2026 | Baseline dibuat | Permintaan PO: timeline paling masuk akal, bisa diintervensi kapan saja | AI |

## Open Items & Blockers
| ID | Isi | Default / usulan | Status |
|---|---|---|---|
| OI-01 | Baseline waktu penyusunan roster | Ukur sebelum P3 | Terbuka |
| OI-02 | HTTPS internal: CA perusahaan atau self-signed | Minta ke IT | Terbuka |
| OI-03 | Foto base64 vs biner terkompresi | Base64, tabel terpisah | Terbuka |
| OI-04 | Status "Sedang Dikerjakan" dikonfirmasi | Disertakan | Terbuka |
| OI-05 | Shift ganda per hari | Tidak didukung | Terbuka |
| OI-06 | Model gratis opencode & limit | Pilih di P0-T02 | **Blocker P0-T02** |
| OI-07 | Lokasi backup di luar server | Bersama IT di P6 | Terbuka |
| OI-08 | Default retensi 12/12/24 bulan | Usulan | Terbuka |
| OI-09 | Floc datar/hierarki | Hierarki opsional | Terbuka |
| OI-10 | Catatan serah terima manual wajib? | Opsional | Terbuka |
| OI-11 | "Realtime" = polling 15 dtk | Ya | Terbuka |
| OI-12 | Pemilik hypercare | PO | Terbuka |
| OI-13 | Mekanisme realtime (SSE + Redis Pub/Sub) | Disetujui PO 9 Nov 2026 | Diputuskan (DEC-22) |
| OI-14 | Host/origin Zabbix untuk CSP `frame-ancestors` | Minta ke IT di P5 | Terbuka |
| OI-15 | TTL cache agregasi dashboard | 2–5 dtk | Terbuka |
| OI-16 | Rotasi/pencabutan token display | Cabut manual + rotasi berkala | Terbuka |
| OI-17 | Host dev tidak punya `make` & gettext (`msgfmt`); Docker daemon off | pip-audit sudah dipasang di venv; Makefile/gettext menunggu tooling | **Blocker P0-T07 verifikasi & P0-T10 ekstraksi .po** |

## Decision Log (ringkas; lengkap di BRD §22)
Django + PostgreSQL + HTMX + Tailwind + Docker · Redis + SSE realtime (bukan WebSocket), dashboard publik/share link + embed Zabbix (DEC-22) · role–permission many-to-many, satu user satu role · hari operasional mulai di Shift 1 · tidak ada fase 2 · opencode gratis + graphify · IT menyetujui IP statis & subdomain lokal · `pip-audit==2.10.1` ditambahkan ke dev requirements untuk audit dependensi per fase.

## Session Log (append-only; simpan 20 terakhir, ringkas yang lebih lama)
Format: `YYYY-MM-DD HH:MM | model | task | hasil | make check | langkah berikutnya`

- 2026-11-09 | perencana | perencanaan | BRD, AGENTS, PROGRESS, skill, command, opencode.json dibuat | n/a | mulai P0-T01
- 2026-11-09 | big-pickle | scaffold + P1-T01/T07/T08 | Django 5.2 LTS scaffold, Custom User, Role/Permission, seed_roles, permission mixin; 16 tes | ruff ✅ · pytest 16 ✅ · makemigrations --check ✅ | lanjut P1-T02
- 2026-11-09 | big-pickle | P1-T02/T03/T04/T12 | auth email/username, password lifecycle, lockout, AuditLog + integrasi auth; 44 tes | ruff ✅ · pytest 44 ✅ · makemigrations --check ✅ | lanjut P1-T05/T06
- 2026-11-09 | big-pickle | P1-T05/T06 | profil (foto 256px, bahasa, tema) + middleware bahasa + kompresi gambar; 55 tes | ruff ✅ · pytest 55 ✅ · makemigrations --check ✅ | lanjut P1-T09/T10
- 2026-11-09 | big-pickle | P1-T09 | UI role CRUD + matriks permission + audit; 64 tes | ruff ✅ · pytest 64 ✅ · makemigrations --check ✅ | lanjut P1-T10/T11
- 2026-11-09 | big-pickle | P1-T10/T11 | UI user (create/edit/reset, tanpa hard-delete) + Super Admin floor + flag role; 76 tes | ruff ✅ · pytest 76 ✅ · makemigrations --check ✅ | lanjut P1-T13
- 2026-11-09 | big-pickle | P1-T13 | Activity Log viewer (filter WIB, paginasi, ekspor CSV aman); 84 tes | ruff ✅ · pytest 84 ✅ · makemigrations --check ✅ | lanjut P1-T14
- 2026-11-09 | big-pickle | P1-T14 | SystemSetting singleton + UI + audit + middleware idle timeout/bahasa default; 92 tes | ruff ✅ · pytest 92 ✅ · makemigrations --check ✅ | lanjut P0-T07/T10 + P1-T15
- 2026-11-09 | big-pickle | P1-T15 (parsial) | coverage total 95%, accounts/audit >85% | coverage ✅ · pytest 92 ✅ | pip-audit/Makefile/gettext terblokir tooling host (OI-17)
- 2026-11-09 | big-pickle | P0-T07/P0-T10 | Makefile + `check_i18n` + skeleton .po id/en; 96 tes | ruff ✅ · pytest 96 ✅ · check_i18n ✅ · makemigrations --check ✅ | P1-T15 pip-audit → P1-T16 tag
- 2026-11-09 | big-pickle | P1-T15 | pip-audit 2.10.1 (bersih) + checklist keamanan `docs/security-checklist.md`; 96 tes | ruff ✅ · pytest 96 ✅ · pip-audit ✅ · coverage 95% ✅ | P1-T16 butuh git init + commit (izin manusia)
- 2026-11-09 | big-pickle | P1-T16 | `git init -b main`, commit awal, tag `phase-1-done` | pytest 96 ✅ · ruff ✅ · i18n ✅ · pip-audit ✅ | mulai P2-T01 master data
