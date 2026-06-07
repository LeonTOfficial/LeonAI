"""Page routes (HTML views)."""
import json

from flask import Blueprint, Response, jsonify, redirect, render_template, session

from services.profile_service import public_profile
from utils.security import login_required

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/")
@login_required
def index():
    is_new_login = session.pop("new_login", False)
    return render_template(
        "index.html",
        is_new_login=is_new_login,
        profile_json=json.dumps(public_profile(), ensure_ascii=False),
    )


@pages_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@pages_bp.route("/manifest.json")
def pwa_manifest():
    return jsonify({
        "name": "LEON AI",
        "short_name": "LEON AI",
        "description": "Persönlicher KI-Assistent",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#eef2fb",
        "theme_color": "#5357ff",
        "orientation": "portrait-primary",
        "icons": [],
    })


@pages_bp.route("/sw.js")
def service_worker():
    sw_code = """
self.addEventListener('install', event => {
  self.skipWaiting();
});
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.map(key => caches.delete(key))))
      .then(() => self.registration.unregister())
      .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', event => {
  event.respondWith(fetch(event.request));
});
"""
    return Response(sw_code, mimetype="application/javascript", headers={"Cache-Control": "no-store"})


_FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="18" fill="#eef1ff"/><g fill="#5357ff"><circle cx="22" cy="22" r="3.3"/><circle cx="32" cy="22" r="3.3"/><circle cx="42" cy="22" r="3.3"/><circle cx="22" cy="32" r="3.3"/><circle cx="32" cy="32" r="3.3"/><circle cx="42" cy="32" r="3.3"/><circle cx="22" cy="42" r="3.3"/><circle cx="32" cy="42" r="3.3"/><circle cx="42" cy="42" r="3.3"/></g></svg>"""


@pages_bp.route("/favicon.ico")
def favicon():
    """Browser fragen oft /favicon.ico an – gleiches Icon wie in index.html."""
    return Response(_FAVICON_SVG, mimetype="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})


@pages_bp.route("/apple-touch-icon.png")
@pages_bp.route("/apple-touch-icon-precomposed.png")
def apple_touch_icon():
    return redirect("/favicon.ico", code=302)
