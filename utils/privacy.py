"""Privacy summary and data purge helpers."""
import os
from pathlib import Path

from config import BACKUP_DIR, LOG_DIR
from models.database import get_db, init_db

PURGE_CONFIRMATION = "LEON-DATEN-LOESCHEN"
PURGE_CATEGORIES = {"chats", "memory", "snippets", "templates", "artifacts", "logs", "backups"}


def privacy_summary() -> dict:
    con = get_db()
    try:
        counts = {
            "rooms": con.execute("SELECT COUNT(*) FROM rooms").fetchone()[0],
            "messages": con.execute("SELECT COUNT(*) FROM messages").fetchone()[0],
            "memory": con.execute("SELECT COUNT(*) FROM memory").fetchone()[0],
            "snippets": con.execute("SELECT COUNT(*) FROM snippets").fetchone()[0],
            "templates": con.execute("SELECT COUNT(*) FROM templates").fetchone()[0],
            "artifacts": con.execute("SELECT COUNT(*) FROM artifact_versions").fetchone()[0],
        }
    finally:
        con.close()
    logs = list(Path(LOG_DIR).glob("leon.log*")) if Path(LOG_DIR).exists() else []
    backups = []
    if Path(BACKUP_DIR).exists():
        backups = list(Path(BACKUP_DIR).glob("chats_*.db"))
        backups += list(Path(BACKUP_DIR).glob("chats_*.db.sha256.json"))
    return {
        **counts,
        "log_files": len(logs),
        "backup_files": len(backups),
        "confirmation": PURGE_CONFIRMATION,
    }


def purge_private_data(categories: list[str], confirmation: str) -> dict:
    if confirmation != PURGE_CONFIRMATION:
        raise ValueError("Bestätigung fehlt")
    selected = set(categories or [])
    if "all" in selected:
        selected = set(PURGE_CATEGORIES)
    selected &= PURGE_CATEGORIES
    if not selected:
        raise ValueError("Keine gültige Kategorie gewählt")

    result = {"purged": sorted(selected)}
    con = get_db()
    try:
        if "chats" in selected:
            con.execute("DELETE FROM messages")
            con.execute("DELETE FROM rooms")
        if "memory" in selected:
            con.execute("DELETE FROM memory")
        if "snippets" in selected:
            con.execute("DELETE FROM snippets")
        if "templates" in selected:
            con.execute("DELETE FROM templates")
        if "artifacts" in selected:
            con.execute("DELETE FROM artifact_versions")
        con.commit()
    finally:
        con.close()

    if "logs" in selected:
        for path in Path(LOG_DIR).glob("leon.log*"):
            try:
                if path.name == "leon.log":
                    path.write_text("", encoding="utf-8")
                else:
                    path.unlink()
            except OSError:
                pass

    if "backups" in selected:
        for pattern in ("chats_*.db", "chats_*.db.sha256.json"):
            for path in Path(BACKUP_DIR).glob(pattern):
                try:
                    path.unlink()
                except OSError:
                    pass

    if "chats" in selected or "templates" in selected:
        init_db()
    return result
