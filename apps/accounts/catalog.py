"""Initial permission catalog and built-in role seeds (BRD section 6)."""

PERMISSION_CATALOG = [
    {"code": "user.view", "name": "View users", "module": "accounts"},
    {"code": "user.manage", "name": "Manage users", "module": "accounts"},
    {"code": "role.manage", "name": "Manage roles and permissions", "module": "accounts"},
    {"code": "settings.manage", "name": "Manage system settings", "module": "core"},
    {"code": "audit.view", "name": "View activity log", "module": "audit"},
    {"code": "master.view", "name": "View master data", "module": "master"},
    {"code": "master.manage", "name": "Manage master data", "module": "master"},
    {"code": "master.import", "name": "Import master data", "module": "master"},
    {"code": "roster.view", "name": "View roster", "module": "roster"},
    {"code": "roster.edit", "name": "Edit roster", "module": "roster"},
    {"code": "roster.import", "name": "Import roster", "module": "roster"},
    {"code": "job.view", "name": "View jobs", "module": "jobs"},
    {"code": "job.create", "name": "Create jobs", "module": "jobs"},
    {"code": "job.edit", "name": "Edit jobs", "module": "jobs"},
    {"code": "job.import", "name": "Import jobs", "module": "jobs"},
    {"code": "job.status_update", "name": "Update job status", "module": "jobs"},
    {"code": "job.cancel_pending", "name": "Set job Pending or Batal", "module": "jobs"},
    {"code": "job.checklist_update", "name": "Update job checklist", "module": "jobs"},
    {"code": "job.reopen", "name": "Reopen finished or cancelled jobs", "module": "jobs"},
    {"code": "dashboard.monitor", "name": "View supervisor dashboard", "module": "dashboard"},
    {"code": "display.view", "name": "View room display", "module": "dashboard"},
]

ADMIN_PERMISSIONS = [
    "user.view",
    "master.view",
    "master.manage",
    "master.import",
    "roster.view",
    "roster.edit",
    "roster.import",
    "job.view",
    "job.create",
    "job.edit",
    "job.import",
    "job.status_update",
    "job.cancel_pending",
    "job.checklist_update",
    "job.reopen",
    "dashboard.monitor",
    "display.view",
]

ROLE_SEEDS = [
    {"code": "super_admin", "name": "Super Admin", "permissions": "*", "is_super_admin": True},
    {"code": "admin", "name": "Admin", "permissions": ADMIN_PERMISSIONS},
    {
        "code": "supervisor",
        "name": "Supervisor",
        "permissions": [
            "master.view",
            "roster.view",
            "job.view",
            "dashboard.monitor",
            "display.view",
        ],
    },
    {
        "code": "teknisi",
        "name": "Teknisi",
        "permissions": [
            "roster.view",
            "job.view",
            "job.status_update",
            "job.cancel_pending",
            "job.checklist_update",
            "display.view",
        ],
    },
    {"code": "display", "name": "Display", "permissions": ["display.view"]},
]
