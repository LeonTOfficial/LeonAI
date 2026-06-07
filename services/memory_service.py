"""Automatic memory extraction from user messages."""
import os
import threading
from datetime import datetime

import requests

from config import DATA_DIR, OLLAMA_BASE
from models.database import get_db
from utils.logging import get_logger

logger = get_logger("leon.memory")

MEMORY_TRIGGERS = [
    "ich heiße", "mein name", "ich bin", "ich arbeite", "ich lerne",
    "ich wohne", "mein lieblings", "ich mag", "ich programmiere",
    "ich studiere", "mein projekt", "ich benutze", "meine schule",
    "ich bin geboren", "ich komme aus", "mein hobby", "ich spiele",
]


def _append_to_akte(fact: str, source: str) -> None:
    try:
        akte_path = os.path.join(DATA_DIR, "Persönliche_Akte.txt")
        with open(akte_path, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%d.%m.%Y %H:%M")
            f.write(f"[{ts}] Neues Detail ({source}): {fact}\n")
    except Exception as e:
        logger.error("Konnte Akte nicht schreiben: %s", e, exc_info=True)


def _memory_worker(room_id: int, user_msg: str, model: str) -> None:
    if not any(t in user_msg.lower() for t in MEMORY_TRIGGERS):
        return
    try:
        r = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json={
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": (
                        f"Enthält diese Nachricht eine persönliche Info? "
                        f"Nur JA oder NEIN.\n{user_msg[:300]}"
                    ),
                }],
                "stream": False,
                "options": {"num_predict": 5},
            },
            timeout=8,
        )
        if r.status_code != 200:
            return
        if "JA" not in r.json().get("message", {}).get("content", "").upper():
            return
    except Exception as e:
        logger.warning("Memory-Check fehlgeschlagen: %s", e)
        return

    fact = user_msg[:300]
    con = get_db()
    try:
        if not con.execute(
            "SELECT id FROM memory WHERE room_id=? AND fact=?", (room_id, fact)
        ).fetchone():
            con.execute(
                "INSERT INTO memory (room_id,fact,created) VALUES (?,?,?)",
                (room_id, fact, datetime.now().isoformat()),
            )
            con.commit()
            _append_to_akte(fact, "Auto")
            logger.info("Memory gespeichert für room_id=%s", room_id)
    except Exception as e:
        logger.error("Memory speichern fehlgeschlagen: %s", e, exc_info=True)
    finally:
        con.close()


def try_save_memory_async(room_id: int, user_msg: str, model: str) -> None:
    threading.Thread(
        target=_memory_worker, args=(room_id, user_msg, model), daemon=True
    ).start()


def add_memory_fact(room_id: int, fact: str) -> dict:
    con = get_db()
    try:
        cur = con.execute(
            "INSERT INTO memory (room_id,fact,created) VALUES (?,?,?)",
            (room_id, fact[:300], datetime.now().isoformat()),
        )
        con.commit()
        _append_to_akte(fact[:300], "Manuell")
        return {"id": cur.lastrowid, "fact": fact}
    finally:
        con.close()
