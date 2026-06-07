"""Chat export in various formats."""
import html
import json
from datetime import datetime

from flask import Response

from models.database import get_db
from utils.text import safe_filename


def export_room(room_id: int, fmt: str = "json") -> Response:
    if fmt not in ("json", "txt", "md", "html"):
        fmt = "json"

    con = get_db()
    room = con.execute("SELECT * FROM rooms WHERE id=?", (room_id,)).fetchone()
    msgs = con.execute(
        "SELECT * FROM messages WHERE room_id=? ORDER BY id ASC", (room_id,)
    ).fetchall()
    con.close()

    if not room:
        return Response(json.dumps({"error": "Nicht gefunden"}), status=404, mimetype="application/json")

    ts = datetime.now().strftime("%d.%m.%Y %H:%M")
    name = safe_filename(room["name"])

    if fmt == "txt":
        lines = [f"=== {room['name']} | {ts} ===\n"]
        for m in msgs:
            role = "Du" if m["role"] == "user" else "LEON AI"
            lines.append(
                f"\n[{m['created'][:16].replace('T', ' ')}] {role}:\n{m['content']}\n"
            )
        return Response(
            "\n".join(lines),
            mimetype="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{name}.txt"'},
        )

    if fmt == "md":
        lines = [f"# {room['name']}\n*{ts} · {room['model']}*\n\n---\n"]
        for m in msgs:
            role = "**Du**" if m["role"] == "user" else "**LEON AI**"
            lines.append(
                f"\n{role} · `{m['created'][:16].replace('T', ' ')}`\n\n{m['content']}\n\n---\n"
            )
        return Response(
            "\n".join(lines),
            mimetype="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{name}.md"'},
        )

    if fmt == "html":
        lines = [
            f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>{html.escape(room['name'])}</title>
<style>body{{font-family:system-ui;max-width:900px;margin:40px auto;background:#0a0b14;color:#ddd8f0;padding:20px}}
.msg{{margin:16px 0;padding:14px;border-radius:10px}}.user{{background:#1a1030;border-left:3px solid #7c3aed}}
.ai{{background:#0d1a24;border-left:3px solid #06b6d4}}.meta{{font-size:.7rem;color:#7a7592;margin-bottom:6px}}
pre{{background:#060810;padding:12px;border-radius:6px;overflow-x:auto}}code{{font-family:monospace}}</style>
</head><body>
<h1 style="color:#a78bfa">💬 {html.escape(room['name'])}</h1>
<p style="color:#7a7592">{ts} · {html.escape(room['model'])}</p><hr style="border-color:#1a1a2e">"""
        ]
        for m in msgs:
            rc = "user" if m["role"] == "user" else "ai"
            rl = "Du" if m["role"] == "user" else "LEON AI"
            ts_m = m["created"][:16].replace("T", " ")
            cont = (
                m["content"]
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            lines.append(
                f'<div class="msg {rc}"><div class="meta">{rl} · {ts_m}</div>'
                f"<pre><code>{cont}</code></pre></div>"
            )
        lines.append("</body></html>")
        return Response(
            "\n".join(lines),
            mimetype="text/html",
            headers={"Content-Disposition": f'attachment; filename="{name}.html"'},
        )

    data = {
        "room": dict(room),
        "exported": datetime.now().isoformat(),
        "messages": [dict(m) for m in msgs],
    }
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": f'attachment; filename="{name}.json"'},
    )
