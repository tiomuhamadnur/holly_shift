"""Tests for image compression (P1-T06)."""
import io

import pytest
from django.core.exceptions import ValidationError
from PIL import Image

from apps.core.images import compress_image


def image_bytes(size=(1600, 1200), fmt="PNG", color=(120, 40, 200)):
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format=fmt)
    return buffer.getvalue()


def test_compress_resizes_and_returns_jpeg():
    content = compress_image(image_bytes(), max_side=256)

    assert content.name == "image.jpg"
    with Image.open(io.BytesIO(content.read())) as result:
        assert result.format == "JPEG"
        assert max(result.size) <= 256


def test_compress_respects_byte_budget():
    content = compress_image(image_bytes((2000, 2000)), max_side=1280, max_bytes=80 * 1024)

    assert len(content.read()) <= 80 * 1024


def test_compress_rejects_corrupt_payload():
    with pytest.raises(ValidationError):
        compress_image(b"definitely not an image")


def test_compress_rejects_unsupported_format():
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10)).save(buffer, format="BMP")

    with pytest.raises(ValidationError):
        compress_image(buffer.getvalue())
