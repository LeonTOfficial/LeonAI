import requests
from config import DEFAULT_MODEL, MAX_CONTEXT_TOKENS, SYSTEM_PROMPT, OLLAMA_BASE
from models.database import get_db
from utils.logging import get_logger

logger = get_logger("leon.chat_service")


def approx_tokens(text: str) -> int:
    if not text:
        return 0
    char_estimate = len(text) / 3.5
    word_estimate = len(text.split()) * 1.3
    return max(1, int((char_estimate + word_estimate) / 2))


def _fallback_title(first_msg: str) -> str:
    words = [
        word.strip(".,:;!?()[]{}\"'`*#")
        for word in (first_msg or "").replace("\n", " ").split()
    ]
    words = [word for word in words if word]
    if not words:
        return "Neuer Chat"
    return " ".join(words[:5])[:40]


def clean_auto_title(raw_title: str, first_msg: str) -> str:
    title = (raw_title or "").strip().strip('"').strip("'").strip()
    if "\n" in title:
        title = next((line.strip() for line in title.splitlines() if line.strip()), "")
    prefixes = (
        "titel:",
        "chat-titel:",
        "chat titel:",
        "vorschlag:",
        "hier ist der titel:",
        "der titel lautet:",
    )
    lowered = title.lower()
    for prefix in prefixes:
        if lowered.startswith(prefix):
            title = title[len(prefix):].strip()
            lowered = title.lower()
            break
    title = " ".join(title.replace("**", "").replace("`", "").split())
    title = title.strip(" .,:;!?-–—\"'")
    if not title or len(title.split()) > 6 or len(title) > 48:
        title = _fallback_title(first_msg)
    return title[:40] or "Neuer Chat"


def generate_auto_title(room_id: int, first_msg: str) -> str:
    prompt = (
        "Erstelle einen kurzen deutschen Chat-Titel.\n"
        "Regeln: 2 bis 5 Wörter, keine Anführungszeichen, keine Erklärung, kein Doppelpunkt.\n"
        f"Erste Nachricht: {first_msg[:300]}"
    )
    try:
        r = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json={"model": "llama3.2:1b", "messages": [{"role": "user", "content": prompt}], "stream": False},
            timeout=30,
        )
        if r.status_code == 200:
            title = clean_auto_title(r.json().get("message", {}).get("content", ""), first_msg)
            if title:
                con = get_db()
                con.execute(
                    "UPDATE rooms SET name=? WHERE id=? AND name='Neuer Chat'",
                    (title, room_id),
                )
                con.commit()
                con.close()
                return title
    except Exception as e:
        logger.error("Auto-Titel fehlgeschlagen: %s", e)
    return ""


def build_messages(room_id: int, user_msg: str, parent_id: int = None) -> tuple:
    con = get_db()
    all_msgs = con.execute(
        "SELECT id, parent_id, role, content, tokens FROM messages WHERE room_id=? ORDER BY id ASC",
        (room_id,),
    ).fetchall()
    
    history_rows = []
    if parent_id is not None:
        msg_dict = {row["id"]: row for row in all_msgs}
        curr_id = parent_id
        while curr_id in msg_dict:
            row = msg_dict[curr_id]
            history_rows.append(row)
            curr_id = row["parent_id"]
    else:
        history_rows = []

    facts = con.execute(
        "SELECT fact FROM memory WHERE room_id=? ORDER BY id DESC LIMIT 15",
        (room_id,),
    ).fetchall()
    room = con.execute(
        "SELECT model,system_prompt FROM rooms WHERE id=?", (room_id,)
    ).fetchone()
    con.close()

    model = room["model"] if room else DEFAULT_MODEL
    custom_sp = room["system_prompt"] if room and room["system_prompt"] else ""
    active_sp = custom_sp.strip() if custom_sp.strip() else SYSTEM_PROMPT

    if facts:
        active_sp += "\n\n📌 Gespeichertes Wissen:\n"
        active_sp += "\n".join(f"  - {f['fact']}" for f in facts)

    messages = [{"role": "system", "content": active_sp}]
    token_budget = MAX_CONTEXT_TOKENS - approx_tokens(active_sp)
    used_tokens = 0
    selected = []
    for row in history_rows:
        t = row["tokens"] or approx_tokens(row["content"])
        if used_tokens + t > token_budget:
            break
        selected.append(row)
        used_tokens += t
    for row in reversed(selected):
        messages.append({
            "role": "user" if row["role"] == "user" else "assistant",
            "content": row["content"],
        })
    messages.append({"role": "user", "content": user_msg})
    return messages, model
