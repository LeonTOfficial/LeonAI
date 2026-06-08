"""LEON AI – Application entry point."""
import os
import socket
import flask.cli

from flask import Flask

from config import (
    AUTH_ENABLED,
    BACKUP_DIR,
    DATA_DIR,
    DEFAULT_MODEL,
    HOST,
    PORT,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    TEMPLATE_FOLDER,
    VISION_MODELS,
    get_secret_key,
)
from models.database import init_db
from routes import register_routes
from services.backup_service import start_backup_thread
from services.ollama_service import get_available_models, ollama_is_running
from services.profile_service import ensure_profile_for_existing_install
from utils.errors import register_error_handlers
from utils.logging import get_logger, setup_logging
from utils.security import get_csrf_token

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


def create_app() -> Flask:
    setup_logging()
    logger = get_logger("leon")

    app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
    app.secret_key = get_secret_key()
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE=os.getenv("SESSION_COOKIE_SAMESITE", "Lax"),
        SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower()
        in ("1", "true", "yes", "on"),
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", str(12 * 1024 * 1024))),
        SEND_FILE_MAX_AGE_DEFAULT=0,
    )

    @app.context_processor
    def security_context():
        return {"csrf_token": get_csrf_token()}

    init_db()
    ensure_profile_for_existing_install()
    register_routes(app)
    register_error_handlers(app)
    start_backup_thread()

    logger.info("LEON AI App initialisiert")
    return app


app = create_app()


if __name__ == "__main__":
    logger = get_logger("leon")
    verbose_startup = os.getenv("LEON_STARTUP_VERBOSE", "0").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    log_path = os.path.join(DATA_DIR, "logs", "leon.log")
    if verbose_startup:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except OSError:
            local_ip = "127.0.0.1"

        print("\n" + "═" * 58)
        print("  ⚡ LEON AI startet...")
        print(f"  📁 Daten:      {DATA_DIR}")
        print(f"  💾 Backups:    {BACKUP_DIR}")
        print(f"  📋 Logs:       {log_path}")
        running = ollama_is_running()
        print(f"  🦙 Ollama:     {'✅ Online' if running else '❌ Offline'}")
        if running:
            models = get_available_models()
            vision = [m for m in models if any(vm in m for vm in VISION_MODELS)]
            print(f"  📦 Modelle:    {', '.join(models[:5])}{'...' if len(models) > 5 else ''}")
            if vision:
                print(f"  🎥 Vision:     {', '.join(vision)}")
        print(f"  🤖 Standard:   {DEFAULT_MODEL}")
        print(f"  🔒 Auth:       {'✅ Aktiviert' if AUTH_ENABLED else '⚠️  Deaktiviert'}")
        if AUTH_ENABLED:
            print("  🔑 Passwort:   gesetzt (nicht im Terminal angezeigt)")
        print(f"  ⚡ Rate Limit: {RATE_LIMIT_REQUESTS} Anfragen / {RATE_LIMIT_WINDOW}s")
        print(f"  🌐 Lokal:      http://localhost:{PORT}")
        if HOST in ("0.0.0.0", "::"):
            print(f"  📱 Netzwerk:   http://{local_ip}:{PORT}")
        else:
            print("  🔒 Netzwerk:   deaktiviert (nur dieser Mac)")
        print("  🧘 Terminal:   ruhig - Details stehen im Logfile")
        print("  ⏹️  Stoppen:    Ctrl+C")
        print("═" * 58 + "\n")
    else:
        print(f"\nLEON AI läuft: http://localhost:{PORT}")
        print(f"Logs: {log_path}")
        print("Beenden: Ctrl+C\n")

    logger.info("Server startet auf %s:%s", HOST, PORT)
    flask.cli.show_server_banner = lambda *args, **kwargs: None
    app.run(debug=False, host=HOST, port=PORT, use_reloader=False)
