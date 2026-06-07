"""Persistent artifact version helpers."""
import hashlib
from datetime import datetime

from models.database import get_db
from utils.text import clean_name, clean_text

MAX_ARTIFACT_HTML_CHARS = 280_000
MAX_ARTIFACT_SOURCE_CHARS = 280_000


def artifact_hash(html: str, source: str = "") -> str:
    payload = (html or "") + "\0" + (source or "")
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()


def normalize_artifact(raw: dict, fallback_index: int = 0) -> dict:
    html = clean_text(raw.get("html", ""), MAX_ARTIFACT_HTML_CHARS)
    source = clean_text(raw.get("source", ""), MAX_ARTIFACT_SOURCE_CHARS)
    title = clean_name(raw.get("title"), f"Artifact {fallback_index + 1}")
    language = clean_text(raw.get("lang") or raw.get("language", ""), 80)
    artifact_key = clean_text(raw.get("key", ""), 240) or artifact_hash(html, source)[:24]
    message_id = raw.get("message_id")
    try:
        message_id = int(message_id) if message_id is not None else None
    except (TypeError, ValueError):
        message_id = None
    if not html:
        raise ValueError("Artifact enthält kein HTML")
    return {
        "message_id": message_id,
        "artifact_key": artifact_key,
        "title": title,
        "language": language,
        "html": html,
        "source": source,
        "content_hash": artifact_hash(html, source),
    }


def list_artifacts(room_id: int) -> list[dict]:
    con = get_db()
    try:
        rows = con.execute(
            "SELECT * FROM artifact_versions WHERE room_id=? ORDER BY id ASC",
            (room_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        con.close()


def delete_artifact(room_id: int, artifact_id: int) -> dict:
    con = get_db()
    try:
        row = con.execute(
            "SELECT id,title FROM artifact_versions WHERE id=? AND room_id=?",
            (artifact_id, room_id),
        ).fetchone()
        if not row:
            raise ValueError("Artifact-Version nicht gefunden")
        con.execute(
            "DELETE FROM artifact_versions WHERE id=? AND room_id=?",
            (artifact_id, room_id),
        )
        con.commit()
        return {"deleted": artifact_id, "title": row["title"], "versions": list_artifacts(room_id)}
    finally:
        con.close()


def save_artifacts(room_id: int, artifacts: list[dict]) -> dict:
    saved = []
    skipped = []
    con = get_db()
    try:
        room = con.execute("SELECT id FROM rooms WHERE id=?", (room_id,)).fetchone()
        if not room:
            raise ValueError("Raum nicht gefunden")
        for index, raw in enumerate(artifacts[:25]):
            artifact = normalize_artifact(raw, index)
            existing = con.execute(
                "SELECT id FROM artifact_versions WHERE room_id=? AND content_hash=?",
                (room_id, artifact["content_hash"]),
            ).fetchone()
            if existing:
                skipped.append(existing["id"])
                continue
            cur = con.execute(
                """
                INSERT INTO artifact_versions
                (room_id,message_id,artifact_key,title,language,html,source,created,content_hash)
                VALUES (?,?,?,?,?,?,?,?,?)
                """,
                (
                    room_id,
                    artifact["message_id"],
                    artifact["artifact_key"],
                    artifact["title"],
                    artifact["language"],
                    artifact["html"],
                    artifact["source"],
                    datetime.now().isoformat(),
                    artifact["content_hash"],
                ),
            )
            saved.append(cur.lastrowid)
        con.commit()
        return {"saved": saved, "skipped": skipped, "versions": list_artifacts(room_id)}
    finally:
        con.close()
