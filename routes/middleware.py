"""Request/response middleware and security headers."""
from flask import g, jsonify, request

from utils.errors import _is_benign_404
from utils.logging import log_activity, new_request_id, set_request_id
from utils.security import csrf_allowed, same_origin_allowed


def register_middleware(app) -> None:
    @app.before_request
    def assign_request_id():
        request_id = request.headers.get("X-Request-ID") or new_request_id()
        g.request_id = request_id[:64]
        set_request_id(g.request_id)

    @app.before_request
    def security_gate():
        if not same_origin_allowed():
            return jsonify({"error": "Ungültiger Ursprung", "request_id": getattr(g, "request_id", "-")}), 403
        if not csrf_allowed():
            return jsonify({"error": "Ungültiger Sicherheits-Token", "request_id": getattr(g, "request_id", "-")}), 403

    @app.before_request
    def log_request():
        path = request.path
        method = request.method
        if path in ("/api/status", "/login"):
            return
        if path == "/":
            log_activity("🌐", "Chat geöffnet", "", "purple")
        elif path == "/dashboard":
            log_activity("📊", "Dashboard geöffnet", "", "blue")
        elif path == "/chat/stream" and method == "POST":
            try:
                data = request.get_json(silent=True) or {}
                msg = data.get("message", "")[:60]
                suffix = "…" if len(data.get("message", "")) > 60 else ""
                log_activity("💬", "Nachricht", f'"{msg}{suffix}"', "cyan")
            except Exception:
                log_activity("💬", "Nachricht gesendet", "", "cyan")
        elif path == "/api/vision" and method == "POST":
            log_activity("📷", "Bild analysiert", "", "purple")
        elif path.endswith("/messages") and method == "GET":
            log_activity("📂", "Chat lädt", "", "dim")
        elif path == "/api/rooms" and method == "POST":
            log_activity("➕", "Neuer Chat erstellt", "", "green")
        elif path.endswith("/favorite") and method == "POST":
            log_activity("⭐", "Favorit geändert", "", "yellow")
        elif path.endswith("/memory") and method == "POST":
            log_activity("🧠", "Erinnerung gespeichert", "", "purple")
        elif path.endswith("/summary") and method == "POST":
            log_activity("📋", "Zusammenfassung generiert", "⏳", "blue")
        elif path.endswith("/export"):
            log_activity("⬇️", "Export", f"Format: {request.args.get('format', 'json')}", "green")
        elif "/memory/" in path and method == "DELETE":
            log_activity("🗑", "Erinnerung gelöscht", "", "yellow")
        elif path.endswith("/clear") and method == "POST":
            log_activity("🧹", "Chatverlauf geleert", "", "yellow")
        elif "/artifacts/" in path and method == "DELETE":
            log_activity("🧩", "Artifact-Version gelöscht", "", "yellow")
        elif "rooms" in path and method == "DELETE":
            log_activity("🗑", "Chat gelöscht", "", "red")
        elif path == "/api/templates" and method == "POST":
            log_activity("📝", "Vorlage gespeichert", "", "green")
        elif "/templates/" in path and method == "DELETE":
            log_activity("🗑", "Vorlage gelöscht", "", "yellow")
        elif path == "/api/search":
            log_activity("🔍", "Suche", f'"{request.args.get("q", "")}"', "cyan")
        elif "model" in path and method == "POST":
            log_activity("🤖", "Modell gewechselt", "", "purple")
        elif path.startswith("/api/rooms") and method == "PATCH":
            log_activity("✏️", "Einstellungen gespeichert", "", "cyan")

    @app.after_request
    def log_response(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Request-ID", getattr(g, "request_id", "-"))
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(self), microphone=(), geolocation=()"
        )
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://cdn.tailwindcss.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob:; "
            "connect-src 'self' https://cdn.jsdelivr.net https://cdn.tailwindcss.com; "
            "worker-src 'self' blob:; "
            "frame-src 'self' data: blob:; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
        )
        if response.status_code >= 400 and not (response.status_code == 404 and _is_benign_404(request.path)):
            log_activity("❌", f"Fehler {response.status_code}", request.path, "red")
        return response

    @app.teardown_request
    def clear_request_context(_exc):
        set_request_id("-")
