"""SSE streaming routes for chat and vision."""
import json
import sqlite3
import threading
from datetime import datetime

import requests
from flask import Blueprint, Response, g, jsonify, request, stream_with_context

from config import DB_PATH, MAX_TEXT_CHARS, OLLAMA_BASE
from models.database import get_db
from services.chat_service import approx_tokens, build_messages, generate_auto_title
from services.memory_service import try_save_memory_async
from services.ollama_service import get_vision_model, ollama_is_running
from utils.logging import get_logger
from utils.media import decode_image_base64
from utils.security import is_rate_limited, login_required
from utils.text import clean_text, is_safe_model_name

chat_bp = Blueprint("chat", __name__)
logger = get_logger("leon.chat")


@chat_bp.route("/chat/stream", methods=["POST"])
@login_required
def chat_stream():
    ip = request.remote_addr
    if is_rate_limited(ip):
        return jsonify({"error": "Zu viele Anfragen. Bitte warte einen Moment."}), 429

    data = request.get_json(silent=True) or {}
    msg = clean_text(data.get("message", ""), MAX_TEXT_CHARS)
    try:
        room_id = int(data.get("room_id", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "Ungültiger Raum"}), 400
    parent_id = data.get("parent_id")
    if parent_id is not None:
        try:
            parent_id = int(parent_id)
        except (TypeError, ValueError):
            parent_id = None
    
    if not msg:
        return jsonify({"error": "Leer"}), 400

    con = get_db()
    room = con.execute("SELECT id FROM rooms WHERE id=?", (room_id,)).fetchone()
    if not room:
        con.close()
        return jsonify({"error": "Raum nicht gefunden"}), 404
    if parent_id is not None:
        parent = con.execute(
            "SELECT id FROM messages WHERE id=? AND room_id=?",
            (parent_id, room_id),
        ).fetchone()
        if not parent:
            con.close()
            return jsonify({"error": "Ungültiger Verlaufspunkt"}), 400
    con.close()
    if not ollama_is_running():
        return jsonify({"error": "ollama_offline", "message": "⚠️ Ollama läuft nicht!"}), 503

    con = get_db()
    user_msg_id = None
    msg_count = 0
    try:
        cur = con.execute(
            "INSERT INTO messages (room_id,parent_id,role,content,created,tokens) VALUES (?,?,?,?,?,?)",
            (room_id, parent_id, "user", msg, datetime.now().isoformat(), approx_tokens(msg)),
        )
        user_msg_id = cur.lastrowid
        con.commit()
        msg_count = con.execute("SELECT COUNT(*) FROM messages WHERE room_id=?", (room_id,)).fetchone()[0]
    except Exception as e:
        logger.error("User-Nachricht speichern fehlgeschlagen: %s", e, exc_info=True)
        return jsonify({"error": "Nachricht konnte nicht gespeichert werden"}), 500
    finally:
        con.close()

    if msg_count == 1:
        threading.Thread(target=generate_auto_title, args=(room_id, msg), daemon=True).start()

    messages, model = build_messages(room_id, msg, parent_id)
    try_save_memory_async(room_id, msg, model)
    request_id = getattr(g, "request_id", "-")

    def generate():
        full = ""
        had_error = False
        start_time = datetime.now()
        try:
            with requests.post(
                f"{OLLAMA_BASE}/api/chat",
                json={"model": model, "messages": messages, "stream": True},
                stream=True,
                timeout=180,
            ) as r:
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        full += token
                        yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.ConnectionError:
            err = "⚠️ Verbindung zu Ollama verloren."
            full = err
            had_error = True
            yield f"data: {json.dumps({'token': err, 'done': False, 'error': True, 'request_id': request_id})}\n\n"
        except requests.exceptions.Timeout:
            err = "⚠️ Zeitüberschreitung."
            full = err
            had_error = True
            yield f"data: {json.dumps({'token': err, 'done': False, 'error': True, 'request_id': request_id})}\n\n"
        except Exception as e:
            logger.error("Chat-Stream Fehler: %s", e, exc_info=True)
            err = f"⚠️ Fehler: {str(e)}"
            full = err
            had_error = True
            yield f"data: {json.dumps({'token': err, 'done': False, 'error': True, 'request_id': request_id})}\n\n"

        elapsed = (datetime.now() - start_time).total_seconds()
        mid = None
        try:
            save = sqlite3.connect(DB_PATH)
            cur = save.execute(
                "INSERT INTO messages (room_id,parent_id,role,content,created,tokens) VALUES (?,?,?,?,?,?)",
                (room_id, user_msg_id, "ai", full, datetime.now().isoformat(), approx_tokens(full)),
            )
            save.commit()
            mid = cur.lastrowid
            save.close()
        except Exception as e:
            logger.error("AI-Nachricht speichern fehlgeschlagen: %s", e, exc_info=True)
        yield f"data: {json.dumps({'token': '', 'done': True, 'msg_id': mid, 'user_msg_id': user_msg_id, 'had_error': had_error, 'elapsed': round(elapsed, 1), 'request_id': request_id})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@chat_bp.route("/chat/vision/stream", methods=["POST"])
@login_required
def chat_vision_stream():
    ip = request.remote_addr
    if is_rate_limited(ip):
        return jsonify({"error": "Zu viele Anfragen. Bitte warte einen Moment."}), 429
    if not ollama_is_running():
        return jsonify({"error": "ollama_offline", "message": "⚠️ Ollama läuft nicht!"}), 503

    data = request.get_json(silent=True) or {}
    try:
        room_id = int(data.get("room_id", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "Ungültiger Raum"}), 400
    parent_id = data.get("parent_id")
    if parent_id is not None:
        try:
            parent_id = int(parent_id)
        except (TypeError, ValueError):
            parent_id = None
    prompt = clean_text(
        data.get("prompt", "Beschreibe dieses Bild auf Deutsch."), 1000
    ) or "Beschreibe dieses Bild auf Deutsch."
    image_name = clean_text(data.get("image_name", "Bild"), 120) or "Bild"
    image_data_url = clean_text(data.get("image_data_url", ""), 12 * 1024 * 1024)
    image_b64 = clean_text(data.get("image_b64", ""), 12 * 1024 * 1024)

    if image_data_url.startswith("data:image/") and "," in image_data_url:
        raw_b64 = image_data_url.split(",", 1)[1]
        stored_image = image_data_url
    else:
        raw_b64 = image_b64
        stored_image = f"data:image/jpeg;base64,{raw_b64}" if raw_b64 else ""
    if not raw_b64:
        return jsonify({"error": "Kein Bild übermittelt"}), 400
    if len(raw_b64) > 10 * 1024 * 1024:
        return jsonify({"error": "Bild zu groß"}), 413
    try:
        decode_image_base64(raw_b64)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    con = get_db()
    room = con.execute("SELECT id, model FROM rooms WHERE id=?", (room_id,)).fetchone()
    if not room:
        con.close()
        return jsonify({"error": "Raum nicht gefunden"}), 404
    if parent_id is not None:
        parent = con.execute(
            "SELECT id FROM messages WHERE id=? AND room_id=?",
            (parent_id, room_id),
        ).fetchone()
        if not parent:
            con.close()
            return jsonify({"error": "Ungültiger Verlaufspunkt"}), 400
    con.close()

    vision_model = get_vision_model(room["model"])
    if not vision_model:
        return jsonify({
            "error": "Kein Vision-Modell installiert. Installiere z.B. mit: ollama pull llava"
        }), 503

    user_text = f"📎 Bild hochgeladen: {image_name}\n{prompt}"
    con = get_db()
    user_msg_id = None
    msg_count = 0
    try:
        cur = con.execute(
            "INSERT INTO messages (room_id,parent_id,role,content,created,tokens,image_b64) VALUES (?,?,?,?,?,?,?)",
            (
                room_id, parent_id, "user", user_text, datetime.now().isoformat(),
                approx_tokens(user_text), stored_image,
            ),
        )
        user_msg_id = cur.lastrowid
        con.commit()
        msg_count = con.execute("SELECT COUNT(*) FROM messages WHERE room_id=?", (room_id,)).fetchone()[0]
    except Exception as e:
        logger.error("Vision-User-Nachricht speichern fehlgeschlagen: %s", e, exc_info=True)
        return jsonify({"error": "Nachricht konnte nicht gespeichert werden"}), 500
    finally:
        con.close()

    if msg_count == 1:
        threading.Thread(target=generate_auto_title, args=(room_id, prompt), daemon=True).start()
    request_id = getattr(g, "request_id", "-")

    def generate():
        full = ""
        had_error = False
        start_time = datetime.now()
        try:
            with requests.post(
                f"{OLLAMA_BASE}/api/chat",
                json={
                    "model": vision_model,
                    "messages": [{"role": "user", "content": prompt, "images": [raw_b64]}],
                    "stream": True,
                },
                stream=True,
                timeout=180,
            ) as r:
                if r.status_code != 200:
                    had_error = True
                    err = f"⚠️ Ollama Vision Fehler: {r.status_code}"
                    full = err
                    yield f"data: {json.dumps({'token': err, 'done': False, 'error': True, 'request_id': request_id})}\n\n"
                else:
                    for line in r.iter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("message", {}).get("content", "")
                            full += token
                            yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.ConnectionError:
            had_error = True
            full = "⚠️ Verbindung zu Ollama verloren."
            yield f"data: {json.dumps({'token': full, 'done': False, 'error': True, 'request_id': request_id})}\n\n"
        except requests.exceptions.Timeout:
            had_error = True
            full = "⚠️ Zeitüberschreitung bei der Bildanalyse."
            yield f"data: {json.dumps({'token': full, 'done': False, 'error': True, 'request_id': request_id})}\n\n"
        except Exception as e:
            logger.error("Vision-Stream Fehler: %s", e, exc_info=True)
            had_error = True
            full = f"⚠️ Fehler: {str(e)}"
            yield f"data: {json.dumps({'token': full, 'done': False, 'error': True, 'request_id': request_id})}\n\n"

        elapsed = (datetime.now() - start_time).total_seconds()
        mid = None
        try:
            save = sqlite3.connect(DB_PATH)
            cur = save.execute(
                "INSERT INTO messages (room_id,parent_id,role,content,created,tokens) VALUES (?,?,?,?,?,?)",
                (room_id, user_msg_id, "ai", full, datetime.now().isoformat(), approx_tokens(full)),
            )
            save.commit()
            mid = cur.lastrowid
            save.close()
        except Exception as e:
            logger.error("Vision-AI-Nachricht speichern fehlgeschlagen: %s", e, exc_info=True)
        yield f"data: {json.dumps({'token': '', 'done': True, 'msg_id': mid, 'user_msg_id': user_msg_id, 'had_error': had_error, 'elapsed': round(elapsed, 1), 'model': vision_model, 'request_id': request_id})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@chat_bp.route("/api/vision/stream", methods=["POST"])
@login_required
def vision_stream():
    ip = request.remote_addr
    if is_rate_limited(ip):
        return jsonify({"error": "Zu viele Anfragen"}), 429
    if not ollama_is_running():
        return jsonify({"error": "Ollama offline"}), 503

    data = request.get_json(silent=True) or {}
    image_b64 = clean_text(data.get("image_b64", ""), 15 * 1024 * 1024)
    prompt = clean_text(data.get("prompt", "Beschreibe dieses Bild auf Deutsch."), 1000)
    model_req = clean_text(data.get("model", ""), 90)

    if not image_b64:
        return jsonify({"error": "Kein Bild"}), 400
    if len(image_b64) > 15 * 1024 * 1024:
        return jsonify({"error": "Bild zu groß"}), 413

    vision_model = get_vision_model(model_req)
    if not vision_model:
        return jsonify({"error": "Kein Vision-Modell installiert"}), 503
    request_id = getattr(g, "request_id", "-")

    def generate():
        try:
            with requests.post(
                f"{OLLAMA_BASE}/api/chat",
                json={
                    "model": vision_model,
                    "messages": [{"role": "user", "content": prompt, "images": [image_b64]}],
                    "stream": True,
                },
                stream=True,
                timeout=180,
            ) as r:
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error("Vision-Stream API Fehler: %s", e, exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'done': True, 'request_id': request_id})}\n\n"
        yield f"data: {json.dumps({'token': '', 'done': True, 'model': vision_model, 'request_id': request_id})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@chat_bp.route("/api/pull", methods=["POST"])
@login_required
def pull_model():
    model = clean_text((request.get_json(silent=True) or {}).get("model", ""), 90)
    if not model:
        return jsonify({"error": "Kein Modell angegeben"}), 400
    if not is_safe_model_name(model):
        return jsonify({"error": "Ungültiger Modellname"}), 400
    if not ollama_is_running():
        return jsonify({"error": "Ollama offline"}), 503
    request_id = getattr(g, "request_id", "-")

    def generate():
        try:
            with requests.post(
                f"{OLLAMA_BASE}/api/pull",
                json={"name": model, "stream": True},
                stream=True,
                timeout=600,
            ) as r:
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        yield f"data: {json.dumps(data)}\n\n"
                        if data.get("status") == "success":
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error("Modell-Pull fehlgeschlagen: %s", e, exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'request_id': request_id})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
