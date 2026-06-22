"""Privacy-safe diagnostics for support and feedback reports."""
import platform
import sys
from datetime import datetime, timezone

from config import APP_VERSION, AUTH_ENABLED, DEFAULT_MODEL, HOST, OLLAMA_BASE, PORT
from services.ollama_service import get_available_models, ollama_is_running
from utils.system_health import collect_health


def _network_mode() -> str:
    return "network" if HOST in ("0.0.0.0", "::") else "local-only"


def collect_diagnostics() -> dict:
    """Return support diagnostics without secrets, prompts, logs, or local paths."""
    running = ollama_is_running()
    models = get_available_models() if running else []
    health = collect_health()
    checks = [
        {
            "name": check.get("name", "unknown"),
            "status": check.get("status", "unknown"),
            "detail": check.get("detail", ""),
        }
        for check in health.get("checks", [])
    ]
    return {
        "app": {
            "name": "LEON AI",
            "version": APP_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "runtime": {
            "python": sys.version.split()[0],
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "configuration": {
            "auth_enabled": AUTH_ENABLED,
            "default_model": DEFAULT_MODEL,
            "host_mode": _network_mode(),
            "port": PORT,
            "ollama_base_configured": bool(OLLAMA_BASE),
        },
        "ollama": {
            "running": running,
            "model_count": len(models),
            "models_preview": models[:8],
        },
        "health": {
            "status": health.get("status", "unknown"),
            "checks": checks,
        },
        "privacy_note": (
            "This diagnostic summary intentionally excludes prompts, chat content, "
            "API keys, .env values, full logs, databases, backups, and local file paths."
        ),
    }
