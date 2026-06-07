"""Input sanitization and validation helpers."""
import re

from config import MAX_NAME_CHARS, MAX_TEXT_CHARS

MODEL_NAME_RE = re.compile(r"^[A-Za-z0-9._:/-]{1,90}$")
SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._ -]+")


def clean_text(value, limit: int = MAX_TEXT_CHARS) -> str:
    return str(value or "").replace("\x00", "").strip()[:limit]


def clean_name(value, default: str = "Neuer Chat") -> str:
    name = clean_text(value, MAX_NAME_CHARS)
    return name or default


def safe_bool(value) -> int:
    return 1 if str(value).lower() in ("1", "true", "yes", "on") else 0


def safe_filename(name: str, default: str = "leon_export") -> str:
    name = SAFE_FILENAME_RE.sub("_", str(name or default)).strip(" ._-")
    return (name[:80] or default)


def is_safe_model_name(model: str) -> bool:
    return bool(MODEL_NAME_RE.fullmatch(str(model or "")))
