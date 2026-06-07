"""System health inspection helpers."""
import os
import sqlite3
from pathlib import Path

from config import BACKUP_DIR, LOG_DIR
from models import database
from services.backup_service import backup_inventory
from services.ollama_service import get_available_models, ollama_is_running


def _ok(name: str, detail: str = "", **extra) -> dict:
    return {"name": name, "status": "ok", "detail": detail, **extra}


def _warn(name: str, detail: str = "", **extra) -> dict:
    return {"name": name, "status": "warn", "detail": detail, **extra}


def _error(name: str, detail: str = "", **extra) -> dict:
    return {"name": name, "status": "error", "detail": detail, **extra}


def collect_health() -> dict:
    checks = []

    try:
        con = sqlite3.connect(database.DB_PATH)
        con.execute("SELECT COUNT(*) FROM rooms").fetchone()
        message_count = con.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        con.close()
        checks.append(_ok("database", "SQLite erreichbar", messages=message_count))
    except Exception as exc:
        checks.append(_error("database", str(exc)))

    log_dir = Path(LOG_DIR)
    log_file = log_dir / "leon.log"
    if log_dir.exists() and os.access(log_dir, os.W_OK):
        size = log_file.stat().st_size if log_file.exists() else 0
        checks.append(_ok("logs", "Log-Verzeichnis beschreibbar", bytes=size))
    else:
        checks.append(_error("logs", "Log-Verzeichnis ist nicht beschreibbar"))

    backup_dir = Path(BACKUP_DIR)
    if backup_dir.exists() and os.access(backup_dir, os.W_OK):
        inventory = backup_inventory()
        verification = inventory.get("latest_verification")
        if not inventory["count"]:
            checks.append(_warn("backups", "Noch kein Backup gefunden", count=0))
        elif verification and verification["status"] == "ok":
            checks.append(_ok(
                "backups",
                f"{inventory['count']} Backups gefunden, letztes geprüft",
                count=inventory["count"],
                latest=inventory["latest"],
                verification=verification,
            ))
        elif verification and verification["status"] == "warn":
            checks.append(_warn(
                "backups",
                f"Letztes Backup braucht neue Prüfsumme: {verification.get('detail', '')}",
                count=inventory["count"],
                latest=inventory["latest"],
                verification=verification,
            ))
        elif verification:
            checks.append(_error(
                "backups",
                f"Letztes Backup nicht verifiziert: {verification.get('detail', '')}",
                count=inventory["count"],
                latest=inventory["latest"],
                verification=verification,
            ))
        else:
            checks.append(_warn("backups", f"{inventory['count']} Backups gefunden", count=inventory["count"]))
    else:
        checks.append(_warn("backups", "Backup-Verzeichnis fehlt oder ist nicht beschreibbar"))

    if ollama_is_running():
        models = get_available_models()
        checks.append(_ok("ollama", f"{len(models)} Modelle verfügbar", models=models[:12]))
    else:
        checks.append(_warn("ollama", "Ollama ist aktuell nicht erreichbar"))

    if all(c["status"] == "ok" for c in checks):
        status = "ok"
    elif any(c["status"] == "error" for c in checks):
        status = "error"
    else:
        status = "warn"
    return {"status": status, "checks": checks}
