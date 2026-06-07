"""Security helpers: rate limiting, origin checks, auth and CSRF protection."""
import hmac
import secrets
import threading
import time
from collections import defaultdict
from functools import wraps
from urllib.parse import urlparse

from flask import jsonify, redirect, request, session, url_for

from config import (
    AUTH_ENABLED,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
)
from services.profile_service import verify_password

_rate_store: dict = defaultdict(list)
_rate_lock = threading.Lock()
CSRF_SESSION_KEY = "_csrf_token"
CSRF_HEADER = "X-CSRF-Token"
MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def check_password(pw: str) -> bool:
    return verify_password(pw)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not AUTH_ENABLED:
            return f(*args, **kwargs)
        if not session.get("authenticated"):
            if request.is_json or request.headers.get("Accept", "").startswith("text/event-stream"):
                return jsonify({"error": "Nicht angemeldet", "redirect": "/login"}), 401
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)

    return decorated


def get_csrf_token() -> str:
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def _request_csrf_token() -> str:
    return (
        request.headers.get(CSRF_HEADER)
        or request.form.get("csrf_token")
        or request.form.get("_csrf_token")
        or ""
    )


def csrf_allowed() -> bool:
    if not AUTH_ENABLED or request.method not in MUTATING_METHODS:
        return True
    if request.path in ("/login", "/setup"):
        expected = session.get(CSRF_SESSION_KEY)
        return bool(expected and hmac.compare_digest(_request_csrf_token(), expected))
    if not session.get("authenticated"):
        return True
    expected = session.get(CSRF_SESSION_KEY)
    return bool(expected and hmac.compare_digest(_request_csrf_token(), expected))


def same_origin_allowed() -> bool:
    if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
        return True
    origin = request.headers.get("Origin") or request.headers.get("Referer")
    if not origin:
        return True
    try:
        o = urlparse(origin)
        origin_host = o.hostname or ""
        request_host = request.host.split(":")[0]
        origin_port = o.port or (443 if o.scheme == "https" else 80)
        request_port = request.environ.get("SERVER_PORT")
        same_host = origin_host == request_host
        same_loopback = origin_host in ("localhost", "127.0.0.1", "::1") and request_host in (
            "localhost",
            "127.0.0.1",
            "::1",
        )
        return (same_host or same_loopback) and str(origin_port) == str(request_port)
    except Exception:
        return False


def is_rate_limited(ip: str) -> bool:
    now = time.time()
    with _rate_lock:
        timestamps = _rate_store[ip]
        _rate_store[ip] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(_rate_store[ip]) >= RATE_LIMIT_REQUESTS:
            return True
        _rate_store[ip].append(now)
    return False
