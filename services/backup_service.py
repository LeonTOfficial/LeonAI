"""Database backup service with integrity manifests."""
import json
import os
import sqlite3
import threading
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path

from config import BACKUP_DIR, MAX_BACKUPS
from models import database
from utils.logging import get_logger

logger = get_logger("leon.backup")
os.makedirs(BACKUP_DIR, exist_ok=True)


def _checksum(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".sha256.json")


def _write_manifest(path: Path) -> dict:
    checksum = _checksum(path)
    manifest = {
        "file": path.name,
        "sha256": checksum,
        "bytes": path.stat().st_size,
        "created": datetime.now().isoformat(timespec="seconds"),
        "version": 1,
    }
    tmp = _manifest_path(path).with_suffix(".tmp")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, _manifest_path(path))
    return manifest


def verify_backup(path: str | Path) -> dict:
    db_path = Path(path)
    manifest_file = _manifest_path(db_path)
    if not db_path.exists():
        return {"status": "error", "file": db_path.name, "detail": "Backup-Datei fehlt"}
    if not manifest_file.exists():
        return {"status": "warn", "file": db_path.name, "detail": "Prüfsumme fehlt"}
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        expected = str(manifest.get("sha256", ""))
        actual = _checksum(db_path)
        if expected and actual == expected:
            return {
                "status": "ok",
                "file": db_path.name,
                "detail": "Prüfsumme gültig",
                "sha256": actual,
                "bytes": db_path.stat().st_size,
            }
        return {
            "status": "error",
            "file": db_path.name,
            "detail": "Prüfsumme stimmt nicht",
            "expected": expected,
            "actual": actual,
        }
    except Exception as exc:
        return {"status": "error", "file": db_path.name, "detail": str(exc)}


def backup_inventory() -> dict:
    backup_dir = Path(BACKUP_DIR)
    backups = sorted(backup_dir.glob("chats_*.db")) if backup_dir.exists() else []
    latest = backups[-1] if backups else None
    return {
        "count": len(backups),
        "files": [p.name for p in backups],
        "latest": latest.name if latest else None,
        "latest_verification": verify_backup(latest) if latest else None,
    }


def _prune_old_backups() -> list[str]:
    removed = []
    backups = sorted(Path(BACKUP_DIR).glob("chats_*.db"))
    while len(backups) > MAX_BACKUPS:
        old = backups.pop(0)
        old.unlink(missing_ok=True)
        _manifest_path(old).unlink(missing_ok=True)
        removed.append(old.name)
        logger.info("Altes Backup entfernt: %s", old.name)
    return removed


def backup_db() -> dict:
    try:
        today = date.today().isoformat()
        dest = Path(BACKUP_DIR) / f"chats_{today}.db"
        created = False
        if not dest.exists():
            tmp = dest.with_suffix(".tmp")
            source = sqlite3.connect(database.DB_PATH)
            target = sqlite3.connect(tmp)
            try:
                source.backup(target)
            finally:
                target.close()
                source.close()
            os.replace(tmp, dest)
            created = True
            logger.info("Backup erstellt: %s", dest)
        manifest = _write_manifest(dest)
        removed = _prune_old_backups()
        verification = verify_backup(dest)
        return {
            "ok": verification["status"] == "ok",
            "created": created,
            "path": str(dest),
            "file": dest.name,
            "sha256": manifest["sha256"],
            "removed": removed,
            "verification": verification,
        }
    except Exception as e:
        logger.error("Backup fehlgeschlagen: %s", e, exc_info=True)
        return {"ok": False, "error": str(e)}


def start_backup_thread() -> None:
    threading.Thread(target=backup_db, daemon=True).start()
