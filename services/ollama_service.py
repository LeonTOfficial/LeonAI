"""Ollama API integration."""
import requests

from config import DEFAULT_MODEL, OLLAMA_BASE, VISION_MODELS
from utils.logging import get_logger

logger = get_logger("leon.ollama")


def ollama_is_running() -> bool:
    try:
        return requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3).status_code == 200
    except Exception as e:
        logger.debug("Ollama nicht erreichbar: %s", e)
        return False


def get_available_models() -> list:
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        if r.status_code == 200:
            return [m["name"] for m in r.json().get("models", [])]
        return [DEFAULT_MODEL]
    except Exception as e:
        logger.warning("Modell-Liste konnte nicht geladen werden: %s", e)
        return [DEFAULT_MODEL]


def get_vision_model(preferred: str = "") -> str:
    available = set(get_available_models())
    if preferred and preferred in available and preferred in VISION_MODELS:
        return preferred
    for vm in VISION_MODELS:
        if vm in available:
            return vm
    return ""
