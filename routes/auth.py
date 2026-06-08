"""Authentication routes."""
from flask import Blueprint, redirect, render_template_string, request, session

from config import AUTH_ENABLED
from services.profile_service import get_first_name, save_first_setup, setup_required
from services.room_service import cleanup_empty_rooms
from utils.logging import get_logger, log_activity
from utils.security import check_password, is_rate_limited

auth_bp = Blueprint("auth", __name__)
logger = get_logger("leon.auth")

LOGIN_HTML = """<!DOCTYPE html>
<html lang="de" data-theme="light">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LEON AI – Login</title>
<meta name="csrf-token" content="{{ csrf_token }}">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20viewBox%3D%270%200%2064%2064%27%3E%3Crect%20width%3D%2764%27%20height%3D%2764%27%20rx%3D%2718%27%20fill%3D%27%23eef1ff%27/%3E%3Cg%20fill%3D%27%235357ff%27%3E%3Ccircle%20cx%3D%2722%27%20cy%3D%2722%27%20r%3D%273.3%27/%3E%3Ccircle%20cx%3D%2732%27%20cy%3D%2722%27%20r%3D%273.3%27/%3E%3Ccircle%20cx%3D%2742%27%20cy%3D%2722%27%20r%3D%273.3%27/%3E%3Ccircle%20cx%3D%2722%27%20cy%3D%2732%27%20r%3D%273.3%27/%3E%3Ccircle%20cx%3D%2732%27%20cy%3D%2732%27%20r%3D%273.3%27/%3E%3Ccircle%20cx%3D%2742%27%20cy%3D%2732%27%20r%3D%273.3%27/%3E%3Ccircle%20cx%3D%2722%27%20cy%3D%2742%27%20r%3D%273.3%27/%3E%3Ccircle%20cx%3D%2732%27%20cy%3D%2742%27%20r%3D%273.3%27/%3E%3Ccircle%20cx%3D%2742%27%20cy%3D%2742%27%20r%3D%273.3%27/%3E%3C/g%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#dfe6f0;--card:rgba(255,255,255,.78);--text:#20232b;--text2:#666b78;--muted:#a1a7b6;--accent:#5357ff;--border:rgba(30,34,50,.08);--shadow:0 24px 70px rgba(89,101,130,.18);--font:'Space Grotesk',system-ui,-apple-system,BlinkMacSystemFont,sans-serif}
html[data-theme="dark"]{--bg:#07080f;--card:rgba(15,23,42,.84);--text:#eef2ff;--text2:#b8c0d9;--muted:#737b95;--accent:#a5b4fc;--border:rgba(255,255,255,.09);--shadow:0 24px 80px rgba(0,0,0,.42)}
*{margin:0;padding:0;box-sizing:border-box}html,body{min-height:100%}body{font-family:var(--font);color:var(--text);display:grid;place-items:center;min-height:100vh;padding:24px;background:radial-gradient(circle at 15% 0%,rgba(255,255,255,.95),transparent 34%),radial-gradient(circle at 78% 12%,rgba(224,224,255,.9),transparent 34%),linear-gradient(135deg,#d9e0ea,#eef2f8 48%,#dbe4f1)}
html[data-theme="dark"] body{background:radial-gradient(circle at 15% 0%,rgba(124,58,237,.20),transparent 34%),radial-gradient(circle at 78% 12%,rgba(34,211,238,.12),transparent 34%),linear-gradient(135deg,#050712,#0b1020 48%,#101827)}
.shell{width:min(1240px,calc(100vw - 48px));min-height:800px;border:1px solid rgba(255,255,255,.72);border-radius:34px;background:linear-gradient(135deg,rgba(244,242,255,.92),rgba(229,239,253,.90));box-shadow:var(--shadow);display:grid;grid-template-columns:1fr 520px;overflow:hidden;margin:auto}
html[data-theme="dark"] .shell{border-color:var(--border);background:linear-gradient(135deg,rgba(11,16,32,.92),rgba(7,17,31,.90))}.left{padding:64px 70px;display:flex;flex-direction:column;justify-content:space-between}.brand{display:flex;align-items:center;gap:12px}.brand-icon{width:34px;height:34px;border-radius:50%;display:grid;place-items:center;background:#f1eeff;color:#5357ff;border:1px solid rgba(83,87,255,.08)}.dot-logo{width:20px;height:20px;display:block;border-radius:50%;background-image:radial-gradient(circle,currentColor 1.05px,transparent 1.25px);background-size:5px 5px;background-position:center;-webkit-mask-image:radial-gradient(circle at center,#000 64%,transparent 66%);mask-image:radial-gradient(circle at center,#000 64%,transparent 66%)}.brand-title{font-size:1.55rem;font-weight:700;letter-spacing:-.03em}.brand-sub{font-size:.8rem;color:var(--text2)}.hero h1{font-size:clamp(3.1rem,5.8vw,4.2rem);line-height:1;letter-spacing:-.05em;margin-bottom:16px}.hero p{color:var(--text2);font-size:1.14rem;max-width:520px;line-height:1.65}.note{font-size:.82rem;color:var(--muted)}.card{background:var(--card);border:1px solid rgba(255,255,255,.86);padding:58px;border-radius:30px;align-self:center;margin-right:54px;box-shadow:0 18px 54px rgba(92,102,130,.14)}html[data-theme="dark"] .card{border-color:var(--border)}.card h2{font-size:1.7rem;margin-bottom:8px}.card p{color:var(--text2);font-size:1rem;margin-bottom:32px}label{display:block;color:var(--text2);font-size:.82rem;margin-bottom:7px}input{width:100%;height:54px;border:1px solid var(--border);border-radius:14px;background:rgba(255,255,255,.65);color:var(--text);padding:0 14px;outline:none;font-size:1rem}html[data-theme="dark"] input{background:rgba(15,23,42,.72)}input:focus{border-color:rgba(83,87,255,.35);box-shadow:0 0 0 4px rgba(83,87,255,.08)}button{width:100%;height:54px;border:0;border-radius:14px;background:#171a1d;color:white;font-weight:700;font-size:1rem;margin-top:18px;cursor:pointer}html[data-theme="dark"] button{background:linear-gradient(135deg,#7c3aed,#06b6d4)}button:hover{transform:translateY(-1px)}.err{display:none;color:#e05252;background:rgba(224,82,82,.08);border:1px solid rgba(224,82,82,.18);border-radius:12px;padding:10px 12px;margin-top:14px;font-size:.86rem}.err.show{display:block}.top-tools{position:fixed;right:22px;top:20px;display:flex;gap:8px;z-index:20}.top-tools button{margin:0;width:auto;height:40px;border:1px solid var(--border);background:rgba(255,255,255,.58);color:var(--text);border-radius:999px;display:grid;place-items:center;box-shadow:0 10px 28px rgba(75,85,110,.12);font-size:.86rem}.theme{width:40px!important}.feature{padding:0 14px!important;grid-auto-flow:column;gap:7px}.feature-modal{position:fixed;inset:0;display:none;place-items:center;padding:24px;background:rgba(7,10,22,.42);backdrop-filter:blur(10px);z-index:30}.feature-modal.show{display:grid}.feature-card{width:min(720px,100%);max-height:min(760px,90vh);overflow:auto;background:var(--card);border:1px solid rgba(255,255,255,.86);border-radius:28px;box-shadow:var(--shadow);padding:28px}.feature-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:18px}.feature-head h2{font-size:1.35rem}.feature-head p{color:var(--text2);line-height:1.55;margin-top:5px}.feature-close{width:36px!important;height:36px!important;border-radius:50%!important;padding:0!important;background:rgba(255,255,255,.52)!important;color:var(--text)!important}.feature-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.feature-item{border:1px solid var(--border);border-radius:16px;padding:13px;background:rgba(255,255,255,.42)}.feature-item strong{display:block;margin-bottom:4px}.feature-item span{color:var(--text2);font-size:.88rem;line-height:1.45}html[data-theme="dark"] .top-tools button,html[data-theme="dark"] .feature-close{background:rgba(15,23,42,.78)!important;color:var(--text)!important}html[data-theme="dark"] .feature-card{border-color:var(--border)}html[data-theme="dark"] .feature-item{background:rgba(15,23,42,.58)}
@media(max-width:800px){.shell{width:min(100%,520px);grid-template-columns:1fr;min-height:auto}.left{padding:30px}.hero{display:none}.card{margin:0 24px 30px;padding:32px}.note{display:none}.feature-grid{grid-template-columns:1fr}.feature{font-size:0}.feature:before{content:'i';font-size:.9rem}}
</style>
<script>try{document.documentElement.dataset.theme=localStorage.getItem('leon-theme')||'light'}catch(e){}</script>
</head>
<body>
<div class="top-tools">
  <button class="feature" type="button" onclick="document.getElementById('feature-modal').classList.add('show')" title="Was kann LEON AI?">i <span>Fähigkeiten</span></button>
  <button class="theme" type="button" onclick="const n=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=n;localStorage.setItem('leon-theme',n);this.textContent=n==='dark'?'☀️':'🌙'">🌙</button>
</div>
<section class="feature-modal" id="feature-modal" onclick="if(event.target===this)this.classList.remove('show')">
  <div class="feature-card">
    <div class="feature-head">
      <div><h2>Was LEON AI kann</h2><p>Dein lokaler KI-Arbeitsbereich für Chat, Code, Vorschau, Analyse und kreative Struktur.</p></div>
      <button class="feature-close" type="button" onclick="document.getElementById('feature-modal').classList.remove('show')">×</button>
    </div>
    <div class="feature-grid">
      <div class="feature-item"><strong>Farbig markieren</strong><span>Texte sicher in Rot, Blau, Grün, Gelb, Lila oder als Marker hervorheben.</span></div>
      <div class="feature-item"><strong>Diagramme & Charts</strong><span>Mermaid-Diagramme und Chart.js-Daten direkt im Chat rendern.</span></div>
      <div class="feature-item"><strong>Artifacts-Vorschau</strong><span>HTML, CSS, JavaScript und Tailwind-Oberflächen live in der Seitenleiste prüfen.</span></div>
      <div class="feature-item"><strong>Python-Sandbox</strong><span>Python-Code im Browser über Pyodide ausführen, ohne dein System direkt anzufassen.</span></div>
      <div class="feature-item"><strong>Branching</strong><span>Alte Nachrichten bearbeiten und ab dort einen neuen Chat-Ast starten.</span></div>
      <div class="feature-item"><strong>Lokal & privat</strong><span>Ollama läuft lokal, Logs und Backups bleiben auf deinem Mac.</span></div>
    </div>
  </div>
</section>
<main class="shell">
  <section class="left">
    <div class="brand"><div class="brand-icon"><span class="dot-logo"></span></div><div><div class="brand-title">LEON AI</div><div class="brand-sub">Lokaler Arbeitsbereich</div></div></div>
    <div class="hero"><h1>{{ hero_heading }}</h1><p>{{ hero_text }}</p></div>
    <div class="note">Port 5001 · lokal auf deinem Mac · Passwort wird nicht im Terminal angezeigt</div>
  </section>
  {% if setup_mode %}
  <form class="card" method="post" action="/setup">
    <h2>Erster Start</h2><p>Richte LEON AI einmalig ein. Danach erscheint nur noch der normale Login.</p>
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <label for="first_name">Vorname</label>
    <input id="first_name" type="text" name="first_name" value="{{ first_name or '' }}" placeholder="Leon" autofocus autocomplete="given-name">
    <label for="password" style="margin-top:14px">Neues Passwort</label>
    <input id="password" type="password" name="password" placeholder="Mindestens 6 Zeichen" autocomplete="new-password">
    <label for="password_confirm" style="margin-top:14px">Passwort wiederholen</label>
    <input id="password_confirm" type="password" name="password_confirm" placeholder="Noch einmal eingeben" autocomplete="new-password">
    <button type="submit">Setup abschließen</button>
    {% if error %}<div class="err show">{{ error }}</div>{% endif %}
  </form>
  {% else %}
  <form class="card" method="post" action="/login">
    <h2>Anmelden</h2><p>Gib dein Passwort ein, um LEON AI zu öffnen.</p>
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <label for="password">Passwort</label>
    <input id="password" type="password" name="password" placeholder="••••••••" autofocus autocomplete="current-password">
    <button type="submit">Einloggen</button>
    {% if error %}<div class="err show">{{ error }}</div>{% endif %}
  </form>
  {% endif %}
</main>
<script>const b=document.querySelector('.theme');try{b.textContent=document.documentElement.dataset.theme==='dark'?'☀️':'🌙'}catch(e){}document.addEventListener('keydown',e=>{if(e.key==='Escape')document.getElementById('feature-modal')?.classList.remove('show')});</script>
</body>
</html>"""


def _render_login(error=None):
    first_name = get_first_name()
    return render_template_string(
        LOGIN_HTML,
        error=error,
        setup_mode=False,
        first_name=first_name,
        hero_heading=f"Willkommen, {first_name}.",
        hero_text="Deine lokale KI-App auf dem MacBook. Schnell, privat und direkt mit Ollama verbunden.",
    )


def _render_setup(error=None, first_name=""):
    return render_template_string(
        LOGIN_HTML,
        error=error,
        setup_mode=True,
        first_name=first_name,
        hero_heading="LEON AI einrichten.",
        hero_text="Lege dein eigenes Passwort fest und personalisiere deinen lokalen KI-Arbeitsbereich.",
    )


@auth_bp.route("/login", methods=["GET"])
def login_page():
    if not AUTH_ENABLED:
        return redirect("/")
    if setup_required():
        return _render_setup()
    return _render_login()


@auth_bp.route("/login", methods=["POST"])
def login_post():
    if setup_required():
        return redirect("/login")
    ip = request.remote_addr or "local"
    if is_rate_limited(f"login:{ip}"):
        return _render_login("Zu viele Versuche. Bitte kurz warten."), 429
    pw = request.form.get("password", "")
    if check_password(pw):
        session["authenticated"] = True
        session["new_login"] = True
        try:
            deleted_empty = cleanup_empty_rooms()
        except Exception as exc:
            deleted_empty = 0
            logger.warning("Leere Chats konnten beim Login nicht aufgeräumt werden: %s", exc, exc_info=True)
        log_activity("🔓", "Login erfolgreich", request.remote_addr, "green")
        if deleted_empty:
            log_activity("🧹", f"{deleted_empty} leere Chats beim Login aufgeräumt", request.remote_addr, "blue")
        return redirect("/")
    log_activity("🔒", "Login fehlgeschlagen", request.remote_addr, "red")
    return _render_login("Falsches Passwort")


@auth_bp.route("/setup", methods=["POST"])
def setup_post():
    if not AUTH_ENABLED:
        return redirect("/")
    if not setup_required():
        return redirect("/login")
    ip = request.remote_addr or "local"
    if is_rate_limited(f"setup:{ip}"):
        return _render_setup("Zu viele Versuche. Bitte kurz warten.", request.form.get("first_name", "")), 429

    ok, error, _profile = save_first_setup(
        request.form.get("first_name", ""),
        request.form.get("password", ""),
        request.form.get("password_confirm", ""),
    )
    if not ok:
        return _render_setup(error, request.form.get("first_name", "")), 400

    session["authenticated"] = True
    session["new_login"] = True
    try:
        deleted_empty = cleanup_empty_rooms()
    except Exception as exc:
        deleted_empty = 0
        logger.warning("Leere Chats konnten nach dem Setup nicht aufgeräumt werden: %s", exc, exc_info=True)
    log_activity("🔐", "Ersteinrichtung abgeschlossen", request.remote_addr, "green")
    if deleted_empty:
        log_activity("🧹", f"{deleted_empty} leere Chats beim Setup aufgeräumt", request.remote_addr, "blue")
    return redirect("/")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
