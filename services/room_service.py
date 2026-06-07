"""Room maintenance helpers."""
from models.database import get_db


def cleanup_empty_rooms() -> int:
    """Delete chats that never received a message."""
    con = get_db()
    try:
        rows = con.execute(
            "SELECT r.id FROM rooms r "
            "LEFT JOIN messages m ON r.id=m.room_id "
            "GROUP BY r.id HAVING COUNT(m.id)=0"
        ).fetchall()
        room_ids = [row["id"] for row in rows]
        for room_id in room_ids:
            con.execute("DELETE FROM artifact_versions WHERE room_id=?", (room_id,))
            con.execute("DELETE FROM memory WHERE room_id=?", (room_id,))
            con.execute("DELETE FROM rooms WHERE id=?", (room_id,))
        con.commit()
        return len(room_ids)
    finally:
        con.close()
