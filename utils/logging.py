"""Structured logging to file and terminal activity output."""
import contextvars
import logging
import os
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler

from config import LOG_DIR

_COLORS = {
    "reset": "\033[0m",
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "blue": "\033[94m",
}

_initialized = False
_request_id = contextvars.ContextVar("request_id", default="-")


def new_request_id() -> str:
    return uuid.uuid4().hex[:12]


def set_request_id(request_id: str | None) -> None:
    _request_id.set(request_id or "-")


def get_request_id() -> str:
    return _request_id.get()


class _RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def setup_logging() -> logging.Logger:
    """Configure structured logging to file and console."""
    global _initialized
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, "leon.log")

    root = logging.getLogger("leon")
    if _initialized:
        return root

    root.setLevel(logging.INFO)
    root.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.INFO)
    file_handler.addFilter(_RequestContextFilter())
    root.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    console_handler.setLevel(logging.WARNING)
    console_handler.addFilter(_RequestContextFilter())
    root.addHandler(console_handler)

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    _initialized = True
    root.info("Logging initialisiert: %s", log_path)
    return root


def get_logger(name: str = "leon") -> logging.Logger:
    if not _initialized:
        setup_logging()
    return logging.getLogger(name)


def log_activity(emoji: str, label: str, detail: str = "", color: str = "cyan") -> None:
    """Human-readable terminal activity (kept for dev UX)."""
    now = datetime.now().strftime("%H:%M:%S")
    c = _COLORS
    t = f"{c['dim']}{now}{c['reset']}"
    lbl = f"{c.get(color, c['cyan'])}{c['bold']}{label}{c['reset']}"
    det = f" {c['dim']}{detail}{c['reset']}" if detail else ""
    print(f"  {emoji}  {t}  {lbl}{det}", flush=True)

    logger = get_logger("leon.activity")
    level = logging.WARNING if color == "red" else logging.INFO
    msg = f"{label}" + (f" | {detail}" if detail else "")
    logger.log(level, msg)
