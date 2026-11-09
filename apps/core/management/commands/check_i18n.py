"""Verify that locale/id and locale/en .po files expose the same msgids."""

import ast
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

LOCALES = ("id", "en")


def _unquote(raw: str) -> str:
    raw = raw.strip()
    if not raw.startswith('"'):
        return ""
    try:
        return ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return raw.strip('"')


def parse_msgids(text: str) -> set[str]:
    """Return every msgid (including plurals) from a .po file body."""
    msgids: set[str] = set()
    current: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("msgid "):
            if current is not None:
                msgids.add(current)
            current = _unquote(stripped[6:])
        elif stripped.startswith("msgid_plural "):
            if current is not None:
                msgids.add(current)
            current = _unquote(stripped[13:])
        elif stripped.startswith('"') and current is not None:
            current += _unquote(stripped)
        elif stripped.startswith(("msgstr", "#")) or stripped == "":
            if current is not None:
                msgids.add(current)
                current = None
    if current is not None:
        msgids.add(current)
    msgids.discard("")
    return msgids


def diff_msgids(ids_by_locale: dict[str, set[str]]) -> tuple[set[str], set[str]]:
    """Return (only_in_id, only_in_en)."""
    only_id = ids_by_locale["id"] - ids_by_locale["en"]
    only_en = ids_by_locale["en"] - ids_by_locale["id"]
    return only_id, only_en


class Command(BaseCommand):
    help = "Fail when locale/id and locale/en .po files drift apart."

    def handle(self, *args, **options):
        locale_root = Path(settings.BASE_DIR) / "locale"
        ids_by_locale: dict[str, set[str]] = {}
        for locale in LOCALES:
            path = locale_root / locale / "LC_MESSAGES" / "django.po"
            if not path.exists():
                raise CommandError(f"Missing locale file: {path}")
            ids_by_locale[locale] = parse_msgids(path.read_text(encoding="utf-8"))

        only_id, only_en = diff_msgids(ids_by_locale)
        if only_id or only_en:
            details = []
            for msgid in sorted(only_id):
                details.append(f"  only in id: {msgid!r}")
            for msgid in sorted(only_en):
                details.append(f"  only in en: {msgid!r}")
            raise CommandError("i18n drift detected:\n" + "\n".join(details))

        self.stdout.write(
            self.style.SUCCESS(
                f"i18n OK ({len(ids_by_locale['id'])} msgids in id/en)"
            )
        )
