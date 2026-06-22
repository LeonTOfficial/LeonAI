"""REST API routes."""
import base64
from datetime import date, datetime, timedelta

import requests
from flask import Blueprint, jsonify, request

from config import APP_VERSION, AUTH_ENABLED, DEFAULT_MODEL, FAST_MODELS, OLLAMA_BASE, VISION_MODELS
from services.artifact_service import delete_artifact, list_artifacts, save_artifacts
from services.backup_service import backup_db, list_backups, restore_backup
from models.database import get_db
from services.chat_service import approx_tokens
from services.export_service import export_room
from services.memory_service import add_memory_fact
from services.ollama_service import get_available_models, get_vision_model, ollama_is_running
from utils.debug_logs import read_debug_logs
from utils.diagnostics import collect_diagnostics
from utils.errors import json_error
from utils.logging import get_logger
from utils.media import decode_image_base64
from utils.privacy import privacy_summary, purge_private_data
from utils.security import is_rate_limited, login_required
from utils.system_health import collect_health
from utils.text import clean_name, clean_text, is_safe_model_name, safe_bool

api_bp = Blueprint("api", __name__, url_prefix="/api")
logger = get_logger("leon.api")


@api_bp.route("/status")
def api_status():
    running = ollama_is_running()
    models = get_available_models() if running else []
    vision_available = [m for m in models if any(vm in m for vm in VISION_MODELS)]
    return jsonify({
        "running": running,
        "models": models,
        "fast_models": FAST_MODELS,
        "vision_models": vision_available,
        "auth_enabled": AUTH_ENABLED,
        "app_version": APP_VERSION,
    })


@api_bp.route("/health", methods=["GET"])
@login_required
def health_check():
    return jsonify(collect_health())


@api_bp.route("/diagnostics", methods=["GET"])
@login_required
def diagnostics():
    return jsonify(collect_diagnostics())


@api_bp.route("/backups/run", methods=["POST"])
@login_required
def run_backup():
    result = backup_db()
    status = 200 if result.get("ok") else 500
    return jsonify(result), status


@api_bp.route("/backups", methods=["GET"])
@login_required
def get_backups():
    return jsonify({"backups": list_backups()})


@api_bp.route("/backups/restore", methods=["POST"])
@login_required
def restore_backup_route():
    data = request.get_json(silent=True) or {}
    file_name = clean_text(data.get("file", ""), 160)
    confirmation = clean_text(data.get("confirmation", ""), 160)
    if not file_name:
        return json_error("Kein Backup ausgewählt", 400)
    if confirmation != file_name:
        return json_error("Bestätigung stimmt nicht mit dem Backup-Dateinamen überein", 400)
    try:
        result = restore_backup(file_name)
        return jsonify(result)
    except ValueError as exc:
        return json_error(str(exc), 400)
    except Exception as exc:
        logger.error("Backup-Wiederherstellung fehlgeschlagen: %s", exc, exc_info=True)
        return json_error("Backup konnte nicht wiederhergestellt werden", 500)


@api_bp.route("/privacy/summary", methods=["GET"])
@login_required
def get_privacy_summary():
    return jsonify(privacy_summary())


@api_bp.route("/privacy/purge", methods=["POST"])
@login_required
def purge_privacy_data():
    data = request.get_json(silent=True) or {}
    categories = data.get("categories", [])
    if isinstance(categories, str):
        categories = [categories]
    try:
        result = purge_private_data(categories, clean_text(data.get("confirmation", ""), 80))
        return jsonify({"ok": True, **result, "summary": privacy_summary()})
    except ValueError as exc:
        return json_error(str(exc), 400)


@api_bp.route("/debug/logs", methods=["GET"])
@login_required
def get_debug_logs():
    level = clean_text(request.args.get("level", ""), 16)
    query = clean_text(request.args.get("q", ""), 120)
    limit = request.args.get("limit", 80, type=int)
    return jsonify(read_debug_logs(limit=limit, level=level, query=query))


@api_bp.route("/log/client-error", methods=["POST"])
@login_required
def log_client_error():
    data = request.get_json(silent=True) or {}
    kind = clean_text(data.get("kind", "frontend"), 40)
    message = clean_text(data.get("message", ""), 600)
    source = clean_text(data.get("source", ""), 220)
    stack = clean_text(data.get("stack", ""), 1800)
    client_request_id = clean_text(data.get("request_id", ""), 80)
    if not message:
        return json_error("Keine Fehlermeldung", 400)
    logger.warning(
        "Client-Fehler | kind=%s | source=%s | related_request_id=%s | message=%s%s",
        kind,
        source or "-",
        client_request_id or "-",
        message,
        f" | stack={stack}" if stack else "",
    )
    return jsonify({"ok": True})


@api_bp.route("/rooms", methods=["GET"])
@login_required
def get_rooms():
    con = get_db()
    rows = con.execute("SELECT * FROM rooms ORDER BY pinned DESC, id ASC").fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@api_bp.route("/rooms", methods=["POST"])
@login_required
def create_room():
    data = request.get_json(silent=True) or {}
    name = clean_name(data.get("name"), "Neuer Chat")
    model = clean_text(data.get("model", DEFAULT_MODEL), 90)
    if not is_safe_model_name(model):
        model = DEFAULT_MODEL
    icon = clean_text(data.get("icon", "💬"), 8)
    color = clean_text(data.get("color", ""), 32)
    con = get_db()
    try:
        cur = con.execute(
            "INSERT INTO rooms (name,model,created,icon,color) VALUES (?,?,?,?,?)",
            (name, model, datetime.now().isoformat(), icon, color),
        )
        con.commit()
        return jsonify({"id": cur.lastrowid, "name": name, "model": model, "icon": icon, "color": color})
    except Exception as e:
        logger.error("Raum erstellen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Raum konnte nicht erstellt werden", 500)
    finally:
        con.close()


@api_bp.route("/rooms/<int:room_id>", methods=["DELETE"])
@login_required
def delete_room(room_id):
    con = get_db()
    try:
        con.execute("DELETE FROM artifact_versions WHERE room_id=?", (room_id,))
        con.execute("DELETE FROM messages WHERE room_id=?", (room_id,))
        con.execute("DELETE FROM memory WHERE room_id=?", (room_id,))
        con.execute("DELETE FROM rooms WHERE id=?", (room_id,))
        con.commit()
        return jsonify({"ok": True})
    except Exception as e:
        logger.error("Raum löschen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Raum konnte nicht gelöscht werden", 500)
    finally:
        con.close()


@api_bp.route("/rooms/<int:room_id>", methods=["PATCH"])
@login_required
def update_room(room_id):
    data = request.get_json(silent=True) or {}
    con = get_db()
    try:
        if "name" in data:
            con.execute("UPDATE rooms SET name=? WHERE id=?", (clean_name(data["name"]), room_id))
        if "pinned" in data:
            con.execute("UPDATE rooms SET pinned=? WHERE id=?", (safe_bool(data["pinned"]), room_id))
        if "system_prompt" in data:
            con.execute("UPDATE rooms SET system_prompt=? WHERE id=?", (clean_text(data["system_prompt"]), room_id))
        if "icon" in data:
            con.execute("UPDATE rooms SET icon=? WHERE id=?", (clean_text(data["icon"], 8), room_id))
        if "color" in data:
            con.execute("UPDATE rooms SET color=? WHERE id=?", (clean_text(data["color"], 32), room_id))
        con.commit()
        return jsonify({"ok": True})
    except Exception as e:
        logger.error("Raum aktualisieren fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Raum konnte nicht aktualisiert werden", 500)
    finally:
        con.close()


@api_bp.route("/rooms/<int:room_id>/model", methods=["POST"])
@login_required
def set_room_model(room_id):
    model = clean_text((request.get_json(silent=True) or {}).get("model", DEFAULT_MODEL), 90)
    if not is_safe_model_name(model):
        return json_error("Ungültiger Modellname", 400)
    con = get_db()
    try:
        con.execute("UPDATE rooms SET model=? WHERE id=?", (model, room_id))
        con.commit()
        return jsonify({"ok": True, "model": model})
    except Exception as e:
        logger.error("Modell setzen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Modell konnte nicht gespeichert werden", 500)
    finally:
        con.close()


@api_bp.route("/rooms/<int:room_id>/clear", methods=["POST"])
@login_required
def clear_room(room_id):
    con = get_db()
    try:
        con.execute("DELETE FROM artifact_versions WHERE room_id=?", (room_id,))
        con.execute("DELETE FROM messages WHERE room_id=?", (room_id,))
        con.execute("DELETE FROM memory WHERE room_id=?", (room_id,))
        con.commit()
        return jsonify({"ok": True})
    except Exception as e:
        logger.error("Verlauf leeren fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Chatverlauf konnte nicht geleert werden", 500)
    finally:
        con.close()


@api_bp.route("/rooms/<int:room_id>/summary", methods=["POST"])
@login_required
def summarize_room(room_id):
    con = get_db()
    room = con.execute("SELECT * FROM rooms WHERE id=?", (room_id,)).fetchone()
    msgs = con.execute(
        "SELECT role,content FROM messages WHERE room_id=? ORDER BY id ASC LIMIT 40",
        (room_id,),
    ).fetchall()
    con.close()
    if not room:
        return json_error("Nicht gefunden", 404)
    if not msgs:
        return jsonify({"summary": "Noch keine Nachrichten."})
    if not ollama_is_running():
        return json_error("Ollama offline", 503)
    history = "\n".join(
        f"{'Nutzer' if m['role'] == 'user' else 'LEON AI'}: {m['content'][:300]}"
        for m in msgs
    )
    prompt = (
        f"Fasse folgenden Chat in maximal 4 Sätzen auf Deutsch zusammen. "
        f"Nenne die wichtigsten Themen:\n\n{history}"
    )
    try:
        r = requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json={"model": room["model"], "messages": [{"role": "user", "content": prompt}], "stream": False},
            timeout=60,
        )
        if r.status_code == 200:
            return jsonify({"summary": r.json().get("message", {}).get("content", "")})
        return json_error("Ollama Fehler", 500)
    except Exception as e:
        logger.error("Zusammenfassung fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Zusammenfassung konnte nicht erstellt werden", 500)


@api_bp.route("/rooms/<int:room_id>/messages", methods=["GET"])
@login_required
def get_messages(room_id):
    con = get_db()
    rows = con.execute(
        "SELECT * FROM messages WHERE room_id=? ORDER BY id ASC", (room_id,)
    ).fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@api_bp.route("/rooms/<int:room_id>/artifacts", methods=["GET"])
@login_required
def get_artifact_versions(room_id):
    con = get_db()
    room = con.execute("SELECT id FROM rooms WHERE id=?", (room_id,)).fetchone()
    con.close()
    if not room:
        return json_error("Raum nicht gefunden", 404)
    return jsonify({"versions": list_artifacts(room_id)})


@api_bp.route("/rooms/<int:room_id>/artifacts", methods=["POST"])
@login_required
def save_artifact_versions(room_id):
    data = request.get_json(silent=True) or {}
    artifacts = data.get("artifacts", [])
    if isinstance(artifacts, dict):
        artifacts = [artifacts]
    if not isinstance(artifacts, list) or not artifacts:
        return json_error("Keine Artefakte übermittelt", 400)
    try:
        return jsonify({"ok": True, **save_artifacts(room_id, artifacts)})
    except ValueError as exc:
        return json_error(str(exc), 400)
    except Exception as exc:
        logger.error("Artifact-Versionen speichern fehlgeschlagen: %s", exc, exc_info=True)
        return json_error("Artifact-Versionen konnten nicht gespeichert werden", 500)


@api_bp.route("/rooms/<int:room_id>/artifacts/<int:artifact_id>", methods=["DELETE"])
@login_required
def delete_artifact_version(room_id, artifact_id):
    try:
        return jsonify({"ok": True, **delete_artifact(room_id, artifact_id)})
    except ValueError as exc:
        return json_error(str(exc), 404)
    except Exception as exc:
        logger.error("Artifact-Version löschen fehlgeschlagen: %s", exc, exc_info=True)
        return json_error("Artifact-Version konnte nicht gelöscht werden", 500)


@api_bp.route("/rooms/<int:room_id>/messages/count", methods=["GET"])
@login_required
def get_message_count(room_id):
    con = get_db()
    count = con.execute(
        "SELECT COUNT(*) FROM messages WHERE room_id=?", (room_id,)
    ).fetchone()[0]
    con.close()
    return jsonify({"count": count})


@api_bp.route("/search")
@login_required
def search_messages():
    q = request.args.get("q", "").strip()
    room_id = request.args.get("room_id", type=int)
    if not q:
        return jsonify([])
    con = get_db()
    try:
        base = (
            "SELECT m.*,r.name as room_name FROM messages m "
            "JOIN rooms r ON m.room_id=r.id WHERE "
        )
        if room_id:
            rows = con.execute(
                base + "m.room_id=? AND m.content LIKE ? ORDER BY m.id DESC LIMIT 40",
                (room_id, f"%{q}%"),
            ).fetchall()
        else:
            rows = con.execute(
                base + "m.content LIKE ? ORDER BY m.id DESC LIMIT 40",
                (f"%{q}%",),
            ).fetchall()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        logger.error("Suche fehlgeschlagen: %s", e, exc_info=True)
        return jsonify([])
    finally:
        con.close()


@api_bp.route("/rooms/<int:room_id>/memory", methods=["GET"])
@login_required
def get_memory(room_id):
    con = get_db()
    rows = con.execute(
        "SELECT * FROM memory WHERE room_id=? ORDER BY id DESC", (room_id,)
    ).fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@api_bp.route("/rooms/<int:room_id>/memory", methods=["POST"])
@login_required
def add_memory(room_id):
    fact = clean_text((request.get_json(silent=True) or {}).get("fact", ""), 300)
    if not fact:
        return json_error("Leer", 400)
    try:
        result = add_memory_fact(room_id, fact)
        return jsonify(result)
    except Exception as e:
        logger.error("Memory hinzufügen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Erinnerung konnte nicht gespeichert werden", 500)


@api_bp.route("/rooms/<int:room_id>/memory/<int:mem_id>", methods=["DELETE"])
@login_required
def delete_memory_item(room_id, mem_id):
    con = get_db()
    try:
        con.execute("DELETE FROM memory WHERE id=? AND room_id=?", (mem_id, room_id))
        con.commit()
        return jsonify({"ok": True})
    except Exception as e:
        logger.error("Memory löschen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Erinnerung konnte nicht gelöscht werden", 500)
    finally:
        con.close()


@api_bp.route("/templates", methods=["GET"])
@login_required
def get_templates():
    con = get_db()
    rows = con.execute("SELECT * FROM templates ORDER BY id ASC").fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@api_bp.route("/templates", methods=["POST"])
@login_required
def create_template():
    data = request.get_json(silent=True) or {}
    label = clean_name(data.get("label"), "Vorlage")
    content = clean_text(data.get("content", ""))
    icon = clean_text(data.get("icon", "💡"), 8)
    if not label or not content:
        return json_error("Fehlende Felder", 400)
    con = get_db()
    try:
        cur = con.execute(
            "INSERT INTO templates (label,content,icon,created) VALUES (?,?,?,?)",
            (label, content, icon, datetime.now().isoformat()),
        )
        con.commit()
        return jsonify({"id": cur.lastrowid, "label": label, "content": content, "icon": icon})
    except Exception as e:
        logger.error("Vorlage erstellen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Vorlage konnte nicht gespeichert werden", 500)
    finally:
        con.close()


@api_bp.route("/templates/<int:tpl_id>", methods=["DELETE"])
@login_required
def delete_template(tpl_id):
    con = get_db()
    try:
        con.execute("DELETE FROM templates WHERE id=?", (tpl_id,))
        con.commit()
        return jsonify({"ok": True})
    except Exception as e:
        logger.error("Vorlage löschen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Vorlage konnte nicht gelöscht werden", 500)
    finally:
        con.close()


@api_bp.route("/snippets", methods=["GET"])
@login_required
def get_snippets():
    con = get_db()
    rows = con.execute("SELECT * FROM snippets ORDER BY id DESC").fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@api_bp.route("/snippets", methods=["POST"])
@login_required
def create_snippet():
    data = request.get_json(silent=True) or {}
    title = clean_name(data.get("title"), "Snippet")
    code = clean_text(data.get("code", ""), 50000)
    lang = clean_text(data.get("language", "plaintext"), 40)
    if not title or not code:
        return json_error("Fehlende Felder", 400)
    con = get_db()
    try:
        cur = con.execute(
            "INSERT INTO snippets (title,code,language,created) VALUES (?,?,?,?)",
            (title, code, lang, datetime.now().isoformat()),
        )
        con.commit()
        return jsonify({"id": cur.lastrowid, "title": title, "code": code, "language": lang})
    except Exception as e:
        logger.error("Snippet erstellen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Snippet konnte nicht gespeichert werden", 500)
    finally:
        con.close()


@api_bp.route("/snippets/<int:snip_id>", methods=["DELETE"])
@login_required
def delete_snippet(snip_id):
    con = get_db()
    try:
        con.execute("DELETE FROM snippets WHERE id=?", (snip_id,))
        con.commit()
        return jsonify({"ok": True})
    except Exception as e:
        logger.error("Snippet löschen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Snippet konnte nicht gelöscht werden", 500)
    finally:
        con.close()


@api_bp.route("/messages/<int:msg_id>/reaction", methods=["POST"])
@login_required
def set_reaction(msg_id):
    reaction = clean_text((request.get_json(silent=True) or {}).get("reaction", ""), 8)
    con = get_db()
    try:
        row = con.execute("SELECT reaction FROM messages WHERE id=?", (msg_id,)).fetchone()
        if not row:
            return json_error("Nicht gefunden", 404)
        new_reaction = "" if row["reaction"] == reaction else reaction
        con.execute("UPDATE messages SET reaction=? WHERE id=?", (new_reaction, msg_id))
        con.commit()
        return jsonify({"reaction": new_reaction})
    except Exception as e:
        logger.error("Reaktion setzen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Reaktion konnte nicht gespeichert werden", 500)
    finally:
        con.close()


@api_bp.route("/messages/<int:msg_id>/favorite", methods=["POST"])
@login_required
def toggle_favorite(msg_id):
    con = get_db()
    try:
        row = con.execute("SELECT favorite FROM messages WHERE id=?", (msg_id,)).fetchone()
        if not row:
            return json_error("Nicht gefunden", 404)
        new = 0 if row["favorite"] else 1
        con.execute("UPDATE messages SET favorite=? WHERE id=?", (new, msg_id))
        con.commit()
        return jsonify({"favorite": bool(new)})
    except Exception as e:
        logger.error("Favorit togglen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Favorit konnte nicht geändert werden", 500)
    finally:
        con.close()


@api_bp.route("/favorites", methods=["GET"])
@login_required
def get_favorites():
    con = get_db()
    rows = con.execute(
        "SELECT m.*,r.name as room_name FROM messages m "
        "JOIN rooms r ON m.room_id=r.id WHERE m.favorite=1 ORDER BY m.id DESC"
    ).fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@api_bp.route("/stats", methods=["GET"])
@login_required
def get_stats():
    days = request.args.get("days", type=int)
    if days is not None:
        days = max(1, min(int(days), 365))
    metric_type = clean_text(request.args.get("type", "all"), 20).lower()
    if metric_type not in {"all", "user", "ai", "favorites"}:
        metric_type = "all"

    def message_filter(alias: str = "messages", include_days: bool = True, extra: str | None = None) -> tuple[str, list]:
        conditions = []
        params = []
        if include_days and days:
            conditions.append(f"{alias}.created >= DATE('now', ?)")
            params.append(f"-{int(days)} days")
        if metric_type == "user":
            conditions.append(f"{alias}.role='user'")
        elif metric_type == "ai":
            conditions.append(f"{alias}.role!='user'")
        elif metric_type == "favorites":
            conditions.append(f"{alias}.favorite=1")
        if extra:
            conditions.append(extra)
        return (" WHERE " + " AND ".join(conditions) if conditions else ""), params

    con = get_db()
    try:
        where_sql, where_params = message_filter()
        total_msgs = con.execute(f"SELECT COUNT(*) FROM messages{where_sql}", where_params).fetchone()[0]
        total_rooms = con.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        fav_where, fav_params = message_filter(extra="messages.favorite=1")
        user_where, user_params = message_filter(extra="messages.role='user'")
        total_favs = con.execute(f"SELECT COUNT(*) FROM messages{fav_where}", fav_params).fetchone()[0]
        user_msgs = con.execute(f"SELECT COUNT(*) FROM messages{user_where}", user_params).fetchone()[0]
        total_mem = con.execute("SELECT COUNT(*) FROM memory").fetchone()[0]
        total_tokens = con.execute(f"SELECT SUM(tokens) FROM messages{where_sql}", where_params).fetchone()[0] or 0
        graph_days = days or 30

        raw = con.execute(
            f"SELECT DATE(created) as day, COUNT(*) as count FROM messages{where_sql} "
            "GROUP BY day ORDER BY day ASC",
            where_params,
        ).fetchall()

        pd_dict = {r["day"]: r["count"] for r in raw}
        today = date.today()
        per_day = [
            {
                "day": (today - timedelta(days=i)).isoformat(),
                "count": pd_dict.get((today - timedelta(days=i)).isoformat(), 0),
            }
            for i in range(graph_days - 1, -1, -1)
        ]
        room_join_extra, room_params = message_filter("m")
        room_join_extra = room_join_extra.replace(" WHERE ", " AND ", 1)
        rooms = con.execute(
            "SELECT r.id,r.name,r.model,COUNT(m.id) as msg_count FROM rooms r "
            f"LEFT JOIN messages m ON r.id=m.room_id{room_join_extra} "
            "GROUP BY r.id ORDER BY msg_count DESC"
            + (", r.pinned DESC" if metric_type != "all" else ""),
            room_params,
        ).fetchall()
        models_used = con.execute(
            "SELECT model,COUNT(*) as cnt FROM rooms GROUP BY model ORDER BY cnt DESC"
        ).fetchall()
        return jsonify({
            "total_messages": total_msgs,
            "total_rooms": total_rooms,
            "total_favorites": total_favs,
            "user_messages": user_msgs,
            "total_memory": total_mem,
            "total_tokens": total_tokens,
            "per_day": per_day,
            "rooms": [dict(r) for r in rooms],
            "models_used": [dict(r) for r in models_used],
            "filter_type": metric_type,
        })
    except Exception as e:
        logger.error("Stats fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Statistiken konnten nicht geladen werden", 500)
    finally:
        con.close()


@api_bp.route("/vision", methods=["POST"])
@login_required
def vision_analyze():
    ip = request.remote_addr
    if is_rate_limited(ip):
        return json_error("Zu viele Anfragen. Bitte warte kurz.", 429)
    if not ollama_is_running():
        return json_error("Ollama ist nicht erreichbar", 503)

    image_b64 = None
    prompt = "Beschreibe was du auf diesem Bild siehst. Antworte auf Deutsch."
    model = ""

    if request.content_type and "multipart/form-data" in request.content_type:
        file = request.files.get("image")
        if not file:
            return json_error("Kein Bild hochgeladen", 400)
        raw = file.read()
        if len(raw) > 10 * 1024 * 1024:
            return json_error("Bild zu groß (max 10 MB)", 413)
        try:
            _raw_check, _kind = decode_image_base64(base64.b64encode(raw).decode("utf-8"))
        except ValueError as e:
            return json_error(str(e), 400)
        image_b64 = base64.b64encode(raw).decode("utf-8")
        prompt = clean_text(request.form.get("prompt", prompt), 1000)
        model = clean_text(request.form.get("model", ""), 90)
    elif request.is_json:
        data = request.get_json(silent=True) or {}
        image_b64 = clean_text(data.get("image_b64", ""), 15 * 1024 * 1024)
        prompt = clean_text(data.get("prompt", prompt), 1000)
        model = clean_text(data.get("model", ""), 90)
        if not image_b64:
            return json_error("Kein Bild (image_b64) übermittelt", 400)
        if len(image_b64) > 15 * 1024 * 1024:
            return json_error("Bild zu groß", 413)
        try:
            decode_image_base64(image_b64)
        except ValueError as e:
            return json_error(str(e), 400)
    else:
        return json_error("Ungültiger Content-Type", 400)

    vision_model = get_vision_model(model)
    if not vision_model:
        return json_error(
            "Kein Vision-Modell installiert. Bitte installiere z.B. "
            "'ollama pull llava' oder 'ollama pull moondream'.",
            503,
        )

    try:
        payload = {
            "model": vision_model,
            "messages": [{"role": "user", "content": prompt, "images": [image_b64]}],
            "stream": False,
            "options": {"num_predict": 512},
        }
        r = requests.post(f"{OLLAMA_BASE}/api/chat", json=payload, timeout=120)
        if r.status_code != 200:
            return json_error("Ollama Vision Fehler", 500, details={"status": r.status_code})
        result = r.json().get("message", {}).get("content", "")
        return jsonify({"result": result, "model": vision_model, "prompt": prompt})
    except requests.exceptions.Timeout:
        return json_error("Zeitüberschreitung beim Bild-Analysieren", 504)
    except Exception as e:
        logger.error("Vision-Analyse fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Bildanalyse konnte nicht abgeschlossen werden", 500)


@api_bp.route("/messages/<int:msg_id>/pin", methods=["POST"])
@login_required
def toggle_pin(msg_id):
    con = get_db()
    try:
        row = con.execute("SELECT pinned FROM messages WHERE id=?", (msg_id,)).fetchone()
        if not row:
            return json_error("Nicht gefunden", 404)
        new = 0 if row["pinned"] else 1
        con.execute("UPDATE messages SET pinned=? WHERE id=?", (new, msg_id))
        con.commit()
        return jsonify({"pinned": bool(new)})
    except Exception as e:
        logger.error("Pin togglen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Pin konnte nicht geändert werden", 500)
    finally:
        con.close()


@api_bp.route("/messages/<int:msg_id>", methods=["PATCH"])
@login_required
def update_message(msg_id):
    data = request.get_json(silent=True) or {}
    content = clean_text(data.get("content", ""))
    if not content:
        return json_error("Leer", 400)
    con = get_db()
    try:
        row = con.execute("SELECT id, room_id FROM messages WHERE id=?", (msg_id,)).fetchone()
        if not row:
            return json_error("Nicht gefunden", 404)
        con.execute(
            "UPDATE messages SET content=?, tokens=? WHERE id=?",
            (content, approx_tokens(content), msg_id),
        )
        con.commit()
        return jsonify({"ok": True, "id": msg_id, "content": content, "tokens": approx_tokens(content)})
    except Exception as e:
        logger.error("Nachricht aktualisieren fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Nachricht konnte nicht aktualisiert werden", 500)
    finally:
        con.close()


@api_bp.route("/rooms/<int:room_id>/messages/after/<int:msg_id>", methods=["DELETE"])
@login_required
def delete_messages_after(room_id, msg_id):
    con = get_db()
    try:
        row = con.execute(
            "SELECT id FROM messages WHERE id=? AND room_id=?", (msg_id, room_id)
        ).fetchone()
        if not row:
            return json_error("Nicht gefunden", 404)
        con.execute(
            "DELETE FROM artifact_versions WHERE room_id=? AND message_id>?",
            (room_id, msg_id),
        )
        cur = con.execute(
            "DELETE FROM messages WHERE room_id=? AND id>?", (room_id, msg_id)
        )
        con.commit()
        return jsonify({"ok": True, "deleted": cur.rowcount})
    except Exception as e:
        logger.error("Nachrichten löschen fehlgeschlagen: %s", e, exc_info=True)
        return json_error("Nachrichten konnten nicht gelöscht werden", 500)
    finally:
        con.close()


@api_bp.route("/rooms/<int:room_id>/export")
@login_required
def export_room_route(room_id):
    fmt = request.args.get("format", "json")
    return export_room(room_id, fmt)
