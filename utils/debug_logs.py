"""Helpers for reading LEON's structured log file."""
import os
import re
from collections import Counter
from pathlib import Path

from config import LOG_DIR

LOG_LINE_RE = re.compile(
    r"^(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| "
    r"(?P<level>[A-Z]+)\s+\| "
    r"(?P<request_id>[^|]+) \| "
    r"(?P<logger>[^|]+) \| "
    r"(?P<source>[^|]+) \| "
    r"(?P<message>.*)$"
)


def _tail_text(path: Path, max_bytes: int = 450_000) -> str:
    if not path.exists():
        return ""
    size = path.stat().st_size
    with path.open("rb") as f:
        if size > max_bytes:
            f.seek(size - max_bytes)
            f.readline()
        return f.read().decode("utf-8", errors="replace")


def parse_log_entries(text: str) -> list[dict]:
    entries: list[dict] = []
    current = None
    for line in text.splitlines():
        match = LOG_LINE_RE.match(line)
        if match:
            current = match.groupdict()
            current["trace"] = []
            for key in ("request_id", "logger", "source", "message"):
                current[key] = current[key].strip()
            entries.append(current)
        elif current and line.strip():
            current["trace"].append(line[:500])
    return entries


def read_debug_logs(limit: int = 80, level: str = "", query: str = "") -> dict:
    limit = max(1, min(int(limit or 80), 200))
    level = str(level or "").upper().strip()
    query = str(query or "").lower().strip()
    log_path = Path(os.path.join(LOG_DIR, "leon.log"))
    entries = parse_log_entries(_tail_text(log_path))
    total_entries = len(entries)

    if level:
        entries = [e for e in entries if e["level"] == level]
    if query:
        entries = [
            e for e in entries
            if query in " ".join([e["message"], e["logger"], e["request_id"], e["source"]]).lower()
        ]

    newest = list(reversed(entries))[:limit]
    all_levels = Counter(e["level"] for e in entries)
    latest_error = next((e for e in reversed(entries) if e["level"] in ("ERROR", "WARNING")), None)
    return {
        "log_path": str(log_path),
        "total_entries": total_entries,
        "returned": len(newest),
        "levels": dict(all_levels),
        "latest_error": latest_error,
        "entries": newest,
    }
