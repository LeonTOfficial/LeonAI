"""Central Flask error handlers."""
import os
import traceback

from flask import g, jsonify, request
from werkzeug.exceptions import HTTPException

from utils.logging import get_logger

# Browser-Anfragen ohne eigene Datei – kein echtes App-Problem
_BENIGN_404_PREFIXES = (
    "/favicon.ico",
    "/apple-touch-icon",
    "/styles.css",
    "/style.css",
    "/script.js",
    "/main.js",
    "/app.js",
    "/leon-ai.jpg",
    "/leon-ai-profile.jpg",
    "/leon-ai-gif.gif",
)


def _is_benign_404(path: str) -> bool:
    return any(path == p or path.startswith(p) for p in _BENIGN_404_PREFIXES)


def json_error(message: str, status: int = 400, *, code: str | None = None, details: dict | None = None):
    """Return a safe JSON error payload with the current request id."""
    payload = {
        "error": message,
        "request_id": getattr(g, "request_id", "-"),
    }
    if code:
        payload["code"] = code
    if details:
        payload["details"] = details
    return jsonify(payload), status


def register_error_handlers(app) -> None:
    logger = get_logger("leon.errors")

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        request_id = getattr(g, "request_id", "-")
        if e.code and e.code >= 500:
            logger.error(
                "HTTP %s | request_id=%s | path=%s | method=%s | desc=%s",
                e.code,
                request_id,
                request.path,
                request.method,
                e.description,
            )
        elif e.code and e.code >= 400 and not (e.code == 404 and _is_benign_404(request.path)):
            logger.warning(
                "HTTP %s | request_id=%s | path=%s | method=%s | desc=%s",
                e.code,
                request_id,
                request.path,
                request.method,
                e.description,
            )
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({
                "error": e.description or "Fehler",
                "code": e.code,
                "request_id": request_id,
            }), e.code
        return e

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e: Exception):
        request_id = getattr(g, "request_id", "-")
        logger.error(
            "Unhandled exception | request_id=%s | path=%s | method=%s | remote=%s | error=%s\n%s",
            request_id,
            request.path,
            request.method,
            request.remote_addr,
            str(e),
            traceback.format_exc(),
        )
        if request.path.startswith("/api/") or request.path.startswith("/chat/") or request.is_json:
            payload = {"error": "Interner Serverfehler", "request_id": request_id}
            if os.getenv("LEON_DEBUG_ERRORS", "false").lower() in ("1", "true", "yes", "on"):
                payload["detail"] = str(e)
            return jsonify(payload), 500
        return "Interner Serverfehler", 500
