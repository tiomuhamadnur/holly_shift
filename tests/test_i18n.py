"""Tests for the i18n sync checker (P0-T10)."""
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.core.management.commands.check_i18n import diff_msgids, parse_msgids


def test_parse_msgids_handles_multiline_and_plural():
    text = """
msgid ""
msgstr ""
"Language: id\\n"

msgid "Hello"
msgstr "Halo"

msgid "One file"
msgid_plural "%(count)s files"
msgstr[0] "Satu file"
msgstr[1] "%(count)s file"
"""

    ids = parse_msgids(text)

    assert ids == {"Hello", "One file", "%(count)s files"}


def test_diff_msgids_reports_both_directions():
    only_id, only_en = diff_msgids({"id": {"a", "b"}, "en": {"b", "c"}})

    assert only_id == {"a"}
    assert only_en == {"c"}


@pytest.mark.django_db
def test_check_i18n_passes_for_project_locales():
    call_command("check_i18n")


@pytest.mark.django_db
def test_check_i18n_detects_drift(settings, tmp_path):
    settings.BASE_DIR = tmp_path
    for locale, msgid in (("id", "Halo"), ("en", "Hello")):
        folder = tmp_path / "locale" / locale / "LC_MESSAGES"
        folder.mkdir(parents=True)
        (folder / "django.po").write_text(
            f'msgid ""\nmsgstr ""\n\nmsgid "{msgid}"\nmsgstr ""\n',
            encoding="utf-8",
        )

    with pytest.raises(CommandError):
        call_command("check_i18n")
