"""SQLite database schema and connection helpers."""
import os
import sqlite3
from datetime import datetime

from config import DATA_DIR, DB_PATH, DEFAULT_MODEL

os.makedirs(DATA_DIR, exist_ok=True)


def _table_columns(cursor: sqlite3.Cursor, table: str) -> set[str]:
    return {row[1] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()}


def _backfill_message_parents(cursor: sqlite3.Cursor) -> None:
    room_ids = [row[0] for row in cursor.execute("SELECT id FROM rooms ORDER BY id ASC").fetchall()]
    for room_id in room_ids:
        rows = cursor.execute(
            "SELECT id,parent_id FROM messages WHERE room_id=? ORDER BY id ASC",
            (room_id,),
        ).fetchall()
        if not rows:
            continue
        has_existing_branch_data = any(row[1] is not None for row in rows)
        if has_existing_branch_data:
            continue
        previous_id = None
        for msg_id, _parent_id in rows:
            cursor.execute(
                "UPDATE messages SET parent_id=? WHERE id=? AND parent_id IS NULL",
                (previous_id, msg_id),
            )
            previous_id = msg_id


def init_db() -> None:
    con = sqlite3.connect(DB_PATH)
    c = con.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        model TEXT NOT NULL DEFAULT 'llama3',
        created TEXT NOT NULL,
        pinned INTEGER DEFAULT 0,
        system_prompt TEXT DEFAULT '',
        color TEXT DEFAULT '',
        icon TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        parent_id INTEGER,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        favorite INTEGER DEFAULT 0,
        created TEXT NOT NULL,
        tokens INTEGER DEFAULT 0,
        reaction TEXT DEFAULT '',
        image_b64 TEXT DEFAULT '',
        pinned INTEGER DEFAULT 0,
        FOREIGN KEY (room_id) REFERENCES rooms(id),
        FOREIGN KEY (parent_id) REFERENCES messages(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        fact TEXT NOT NULL,
        created TEXT NOT NULL,
        FOREIGN KEY (room_id) REFERENCES rooms(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT NOT NULL,
        content TEXT NOT NULL,
        icon TEXT DEFAULT '💡',
        created TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS snippets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        code TEXT NOT NULL,
        language TEXT DEFAULT 'plaintext',
        created TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS artifact_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        message_id INTEGER,
        artifact_key TEXT NOT NULL,
        title TEXT NOT NULL,
        language TEXT DEFAULT '',
        html TEXT NOT NULL,
        source TEXT DEFAULT '',
        created TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        FOREIGN KEY (room_id) REFERENCES rooms(id),
        FOREIGN KEY (message_id) REFERENCES messages(id),
        UNIQUE(room_id, content_hash)
    )""")
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_artifact_versions_room "
        "ON artifact_versions(room_id, id)"
    )

    message_columns = _table_columns(c, "messages")
    added_parent_id = "parent_id" not in message_columns

    migrations = [
        "ALTER TABLE rooms    ADD COLUMN pinned INTEGER DEFAULT 0",
        "ALTER TABLE rooms    ADD COLUMN system_prompt TEXT DEFAULT ''",
        "ALTER TABLE rooms    ADD COLUMN color TEXT DEFAULT ''",
        "ALTER TABLE rooms    ADD COLUMN icon TEXT DEFAULT ''",
        "ALTER TABLE messages ADD COLUMN tokens INTEGER DEFAULT 0",
        "ALTER TABLE messages ADD COLUMN reaction TEXT DEFAULT ''",
        "ALTER TABLE messages ADD COLUMN image_b64 TEXT DEFAULT ''",
        "ALTER TABLE messages ADD COLUMN pinned INTEGER DEFAULT 0",
        "ALTER TABLE messages ADD COLUMN parent_id INTEGER REFERENCES messages(id)",
    ]
    for sql in migrations:
        try:
            c.execute(sql)
        except sqlite3.OperationalError:
            pass

    if added_parent_id:
        _backfill_message_parents(c)

    if c.execute("SELECT COUNT(*) FROM rooms").fetchone()[0] == 0:
        c.execute(
            "INSERT INTO rooms (name,model,created,icon) VALUES (?,?,?,?)",
            ("Allgemein", DEFAULT_MODEL, datetime.now().isoformat(), "💬"),
        )

    if c.execute("SELECT COUNT(*) FROM templates").fetchone()[0] == 0:
        defaults = [
            ("💡", "Konzept erklären", "Erkläre mir einfach und verständlich: "),
            ("🐍", "Python Code", "Schreib mir Python Code für: "),
            ("🔍", "Analysieren", "Analysiere und verbessere folgendes: "),
            ("✍️", "Text erstellen", "Erstelle einen professionellen Text über: "),
            ("🐛", "Debuggen", "Debugge diesen Code und erkläre den Fehler:\n\n"),
            ("🌍", "Übersetzen", "Übersetze folgenden Text ins Deutsche: "),
            ("📊", "Daten analysieren", "Analysiere diese Daten und erstelle eine Zusammenfassung:\n\n"),
            ("🧪", "Unit Tests", "Schreib Unit Tests für folgenden Code:\n\n"),
            ("📧", "E-Mail schreiben", "Schreib eine professionelle E-Mail zu folgendem Thema: "),
            ("🗺️", "Plan erstellen", "Erstelle einen detaillierten Plan für: "),
        ]
        for icon, label, content in defaults:
            c.execute(
                "INSERT INTO templates (label,content,icon,created) VALUES (?,?,?,?)",
                (label, content, icon, datetime.now().isoformat()),
            )

    con.commit()
    con.close()


def get_db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con
