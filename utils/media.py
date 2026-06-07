"""Small media validation helpers."""
import base64
import binascii


def decode_image_base64(value: str, max_bytes: int = 10 * 1024 * 1024) -> tuple[bytes, str]:
    """Decode and lightly validate browser-provided image data."""
    text = str(value or "")
    if "," in text and text.lower().startswith("data:image/"):
        text = text.split(",", 1)[1]
    if not text:
        raise ValueError("Kein Bild übermittelt")
    try:
        raw = base64.b64decode(text, validate=True)
    except binascii.Error as exc:
        raise ValueError("Bilddaten sind ungültig") from exc
    if len(raw) > max_bytes:
        raise ValueError("Bild zu groß")
    signatures = (
        (b"\xff\xd8\xff", "jpeg"),
        (b"\x89PNG\r\n\x1a\n", "png"),
        (b"GIF87a", "gif"),
        (b"GIF89a", "gif"),
    )
    for prefix, kind in signatures:
        if raw.startswith(prefix):
            return raw, kind
    if raw.startswith(b"RIFF") and len(raw) >= 12 and raw[8:12] == b"WEBP":
        return raw, "webp"
    raise ValueError("Nur PNG, JPEG, GIF oder WebP Bilder sind erlaubt")
