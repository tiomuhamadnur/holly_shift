"""Tests for the profile screen and per-user language (P1-T05)."""
import io

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import translation
from PIL import Image

from apps.accounts.forms import ProfileForm
from apps.accounts.middleware import UserLanguageMiddleware
from apps.accounts.models import User
from apps.audit.models import AuditLog


@pytest.fixture
def user(db):
    return User.objects.create_user(username="budi", password="S3cretPass!")


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


def upload(size=(800, 800), fmt="JPEG"):
    buffer = io.BytesIO()
    Image.new("RGB", size, (30, 60, 90)).save(buffer, format=fmt)
    return SimpleUploadedFile(f"avatar.{fmt.lower()}", buffer.getvalue(), content_type="image/jpeg")


@pytest.mark.django_db
def test_profile_requires_login(client):
    response = client.get(reverse("profile"))

    assert response.status_code == 302
    assert reverse("login") in response["Location"]


def test_update_language_and_theme(client, user):
    client.force_login(user)

    response = client.post(reverse("profile"), {"language": "en", "theme": "dark"})

    assert response.status_code == 302
    user.refresh_from_db()
    assert user.language == "en"
    assert user.theme == "dark"


def test_uploaded_photo_is_compressed(client, user):
    client.force_login(user)

    response = client.post(
        reverse("profile"),
        {"language": "id", "theme": "system", "photo": upload()},
    )

    assert response.status_code == 302
    user.refresh_from_db()
    assert user.photo
    with Image.open(user.photo.path) as photo:
        assert max(photo.size) <= 256


def test_update_writes_audit_entry(client, user):
    client.force_login(user)

    client.post(reverse("profile"), {"language": "en", "theme": "dark"})

    entry = AuditLog.objects.filter(action=AuditLog.Action.UPDATE, entity="User").first()
    assert entry is not None
    assert entry.before["language"] == "id"
    assert entry.after["language"] == "en"


def test_non_image_upload_is_rejected(client, user):
    client.force_login(user)
    bogus = SimpleUploadedFile("notes.txt", b"hello", content_type="text/plain")

    response = client.post(
        reverse("profile"), {"language": "id", "theme": "system", "photo": bogus}
    )

    assert response.status_code == 200
    assert response.context["form"].errors["photo"]
    user.refresh_from_db()
    assert not user.photo


@pytest.mark.django_db
def test_profile_form_rejects_oversize_file():
    class Oversize:
        size = 6 * 1024 * 1024

    form = ProfileForm()
    form.cleaned_data = {"photo": Oversize()}

    with pytest.raises(ValidationError):
        form.clean_photo()


def test_user_language_middleware_activates_saved_language(db, rf):
    user = User.objects.create_user(username="lang", password="S3cretPass!", language="en")
    request = rf.get("/")
    request.user = user
    seen = {}

    def get_response(_request):
        seen["language"] = translation.get_language()
        return "ok"

    translation.deactivate_all()
    try:
        UserLanguageMiddleware(get_response)(request)
    finally:
        translation.deactivate_all()

    assert seen["language"] == "en"
