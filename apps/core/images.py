"""Image compression helper (P1-T06).

Used for profile photos and (later) job attachments. Output is always a compact
JPEG so storage and bandwidth stay bounded on the internal network.
"""
import io

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from PIL import Image, ImageOps

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
DEFAULT_MAX_SIDE = 1280
DEFAULT_MAX_BYTES = 300 * 1024


def _flatten_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode == "RGB":
        return image
    if image.mode in {"RGBA", "LA", "P"}:
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.split()[-1])
        return background
    return image.convert("RGB")


def _encode(image: Image.Image, quality: int, max_bytes: int) -> bytes:
    payload = b""
    for current in range(quality, 19, -10):
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=current, optimize=True)
        payload = buffer.getvalue()
        if len(payload) <= max_bytes:
            return payload
    return payload


def compress_image(
    source,
    *,
    max_side: int = DEFAULT_MAX_SIDE,
    quality: int = 75,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> ContentFile:
    """Resize and re-encode an image to a compact JPEG.

    Raises ``ValidationError`` when the payload is empty, corrupt, or not a
    supported format (JPEG/PNG/WebP).
    """
    data = source.read() if hasattr(source, "read") else source
    if not isinstance(data, (bytes, bytearray)) or not data:
        raise ValidationError(_("Empty or unreadable image."))

    try:
        with Image.open(io.BytesIO(data)) as opened:
            if opened.format not in ALLOWED_FORMATS:
                raise ValidationError(
                    _("Only JPEG, PNG or WebP images are allowed.")
                )
            image = _flatten_to_rgb(ImageOps.exif_transpose(opened))
            image.thumbnail((max_side, max_side))
            payload = _encode(image, quality, max_bytes)
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError(_("Unsupported or corrupt image.")) from exc

    return ContentFile(payload, name="image.jpg")
