"""Small local profile store for first-run setup and login credentials."""
import hashlib
import hmac
import json
import os
import re
from datetime import datetime

from config import DATA_DIR, PASSWORD_HASH
from models.database import get_db

PROFILE_PATH = os.path.join(DATA_DIR, "profile.json")
MIN_PASSWORD_LENGTH = 6


def _password_hash(password: str) -> str:
    return hashlib.sha256(str(password or "").encode("utf-8")).hexdigest()


def _clean_first_name(first_name: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(first_name or "").strip())
    cleaned = cleaned.replace("<", "").replace(">", "")
    return cleaned[:32]


def _write_profile(profile: dict) -> None:
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    tmp_path = f"{PROFILE_PATH}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, PROFILE_PATH)
    try:
        os.chmod(PROFILE_PATH, 0o600)
    except OSError:
        pass


def load_profile() -> dict:
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            profile = json.load(f)
        return profile if isinstance(profile, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def is_setup_complete() -> bool:
    profile = load_profile()
    return bool(profile.get("setup_complete") and profile.get("password_hash"))


def _has_existing_user_data() -> bool:
    try:
        con = get_db()
        try:
            messages = con.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            non_default_rooms = con.execute(
                "SELECT COUNT(*) FROM rooms WHERE name <> ?",
                ("Allgemein",),
            ).fetchone()[0]
            artifacts = con.execute("SELECT COUNT(*) FROM artifact_versions").fetchone()[0]
            memories = con.execute("SELECT COUNT(*) FROM memory").fetchone()[0]
            return any((messages, non_default_rooms, artifacts, memories))
        finally:
            con.close()
    except Exception:
        return False


def ensure_profile_for_existing_install() -> None:
    """Keep upgraded installs usable without forcing a surprise setup screen."""
    if is_setup_complete() or not _has_existing_user_data():
        return
    _write_profile({
        "setup_complete": True,
        "first_name": "Leon",
        "password_hash": PASSWORD_HASH,
        "created": datetime.now().isoformat(),
        "migrated_from_env_password": True,
    })


def setup_required() -> bool:
    return not is_setup_complete()


def save_first_setup(first_name: str, password: str, password_confirm: str) -> tuple[bool, str, dict]:
    cleaned_name = _clean_first_name(first_name)
    if not cleaned_name:
        return False, "Bitte gib deinen Vornamen ein.", {}
    if len(str(password or "")) < MIN_PASSWORD_LENGTH:
        return False, f"Das Passwort muss mindestens {MIN_PASSWORD_LENGTH} Zeichen lang sein.", {}
    if password != password_confirm:
        return False, "Die Passwörter stimmen nicht überein.", {}

    profile = {
        "setup_complete": True,
        "first_name": cleaned_name,
        "password_hash": _password_hash(password),
        "created": datetime.now().isoformat(),
        "migrated_from_env_password": False,
    }
    _write_profile(profile)
    return True, "", profile


def get_password_hash() -> str:
    profile = load_profile()
    if profile.get("setup_complete") and profile.get("password_hash"):
        return str(profile["password_hash"])
    return PASSWORD_HASH


def verify_password(password: str) -> bool:
    return hmac.compare_digest(_password_hash(password), get_password_hash())


def get_first_name(default: str = "Leon") -> str:
    name = _clean_first_name(load_profile().get("first_name", ""))
    return name or default


def public_profile() -> dict:
    return {"first_name": get_first_name()}
