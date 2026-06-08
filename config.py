"""Central application configuration."""
import os
import hashlib

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_TEMPLATE_FOLDER = os.getenv("TEMPLATE_FOLDER")
if not _TEMPLATE_FOLDER:
    _TEMPLATE_FOLDER = (
        "template"
        if (
            os.path.isdir(os.path.join(BASE_DIR, "template"))
            and not os.path.isdir(os.path.join(BASE_DIR, "templates"))
        )
        else "templates"
    )

DATA_DIR = os.path.join(BASE_DIR, os.getenv("DATA_DIR", "data"))
BACKUP_DIR = os.path.join(BASE_DIR, os.getenv("BACKUP_DIR", "backup"))
LOG_DIR = os.path.join(DATA_DIR, "logs")
DB_PATH = os.path.join(DATA_DIR, "chats.db")

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
PORT = int(os.getenv("PORT", 5001))
MAX_BACKUPS = int(os.getenv("MAX_BACKUPS", 7))
HOST = os.getenv("HOST", "127.0.0.1")

RAW_PASSWORD = os.getenv("LEON_PASSWORD", "leon2026")
PASSWORD_HASH = hashlib.sha256(RAW_PASSWORD.encode()).hexdigest()
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "true").lower() in ("1", "true", "yes", "on")

RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT", 30))
RATE_LIMIT_WINDOW = 60

MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", 12000))
MAX_NAME_CHARS = 80
MAX_CONTEXT_TOKENS = 6000

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    (
        "Du bist LEON AI, ein intelligenter persönlicher Assistent. "
        "Antworte IMMER auf Deutsch, egal in welcher Sprache der Nutzer schreibt. "
        "Wenn der Nutzer Deutsch schreibt, bleibe konsequent bei Deutsch: keine englischen Überschriften, keine englischen Zusammenfassungen und keine englischen Standardfloskeln, außer bei Code, APIs, Dateinamen oder klar etablierten Fachbegriffen. "
        "Sei präzise, freundlich und direkt. "
        "Wenn du Code schreibst, nutze immer Code-Blöcke mit der richtigen Sprache. "
        "Nutze Markdown für Formatierungen, wo es sinnvoll ist. "
        "Wenn ein Ablauf, System oder Prozess leichter visuell verständlich ist, nutze einen mermaid-Codeblock. "
        "Wenn Zahlen, Messwerte oder Vergleiche vorkommen, erstelle Charts direkt im Chat als Codeblock mit der Sprache `chart` und gültigem Chart.js-JSON. Schreibe niemals nur das Wort chart-Codeblock. Beispiel:\n```chart\n{\"type\":\"bar\",\"data\":{\"labels\":[\"A\",\"B\"],\"datasets\":[{\"label\":\"Werte\",\"data\":[3,5]}]}}\n```. "
        "Für farbige Textmarkierungen im Chat nutze sichere Tags wie [rot]Text[/rot], [blau]Text[/blau], [gruen]Text[/gruen], [gelb]Text[/gelb], [lila]Text[/lila] oder [mark]Text[/mark]. Nutze beim Schließen möglichst dieselbe deutsche Farbe, also nicht gemischt wie [rot]Text[/red]. "
        "Wenn du Webseiten oder UI-Prototypen erstellst, liefere vollständiges HTML und nutze gern Tailwind-Klassen; die Vorschau lädt Tailwind automatisch. "
        "Vermeide unnötige externe Skripte und erkläre kurz, wenn externe Ressourcen wirklich nötig sind. "
        "Leon.T hat dich erschaffen."
    ),
)

VISION_MODELS = [
    "llava", "llava:7b", "llava:13b", "llava:34b",
    "llava-phi3", "moondream", "bakllava", "minicpm-v",
    "llava-llama3", "cogvlm",
]

FAST_MODELS = [
    {"name": "phi3:mini", "label": "Phi-3 Mini", "speed": "⚡ Sehr schnell", "desc": "Microsoft – sehr effizient", "vision": False},
    {"name": "phi3:medium", "label": "Phi-3 Medium", "speed": "⚡ Schnell", "desc": "Microsoft – gute Balance", "vision": False},
    {"name": "phi4-mini", "label": "Phi-4 Mini", "speed": "⚡ Schnell", "desc": "Microsoft – neueste Gen", "vision": False},
    {"name": "gemma3:1b", "label": "Gemma3 1B", "speed": "⚡ Sehr schnell", "desc": "Google – ultra-leicht", "vision": False},
    {"name": "gemma3:4b", "label": "Gemma3 4B", "speed": "⚡ Schnell", "desc": "Google – kompakt", "vision": False},
    {"name": "gemma3:12b", "label": "Gemma3 12B", "speed": "🔥 Mittel", "desc": "Google – ausgewogen", "vision": False},
    {"name": "gemma3:27b", "label": "Gemma3 27B", "speed": "🧠 Langsam", "desc": "Google – leistungsstark", "vision": False},
    {"name": "qwen2.5:0.5b", "label": "Qwen2.5 0.5B", "speed": "⚡ Ultra", "desc": "Alibaba – extrem klein", "vision": False},
    {"name": "qwen2.5:1.5b", "label": "Qwen2.5 1.5B", "speed": "⚡ Sehr schnell", "desc": "Alibaba – sehr schnell", "vision": False},
    {"name": "qwen2.5:3b", "label": "Qwen2.5 3B", "speed": "⚡ Schnell", "desc": "Alibaba – effizient", "vision": False},
    {"name": "qwen2.5:7b", "label": "Qwen2.5 7B", "speed": "🔥 Mittel", "desc": "Alibaba – stark", "vision": False},
    {"name": "qwen2.5:14b", "label": "Qwen2.5 14B", "speed": "🔥 Mittel", "desc": "Alibaba – sehr stark", "vision": False},
    {"name": "mistral:7b", "label": "Mistral 7B", "speed": "🔥 Mittel", "desc": "Mistral AI – klassisch", "vision": False},
    {"name": "mistral-nemo", "label": "Mistral Nemo", "speed": "🔥 Mittel", "desc": "Mistral AI – kompakt", "vision": False},
    {"name": "llama3.2:1b", "label": "Llama3.2 1B", "speed": "⚡ Sehr schnell", "desc": "Meta – sehr schnell", "vision": False},
    {"name": "llama3.2:3b", "label": "Llama3.2 3B", "speed": "⚡ Schnell", "desc": "Meta – schnell & gut", "vision": False},
    {"name": "llama3.1:8b", "label": "Llama3.1 8B", "speed": "🔥 Mittel", "desc": "Meta – ausgewogen", "vision": False},
    {"name": "llama3.3:70b", "label": "Llama3.3 70B", "speed": "🧠 Langsam", "desc": "Meta – sehr leistungsstark", "vision": False},
    {"name": "deepseek-r1:1.5b", "label": "DeepSeek-R1 1.5B", "speed": "⚡ Sehr schnell", "desc": "DeepSeek – Reasoning", "vision": False},
    {"name": "deepseek-r1:7b", "label": "DeepSeek-R1 7B", "speed": "🔥 Mittel", "desc": "DeepSeek – Reasoning", "vision": False},
    {"name": "deepseek-r1:14b", "label": "DeepSeek-R1 14B", "speed": "🔥 Mittel", "desc": "DeepSeek – Reasoning+", "vision": False},
    {"name": "codellama:7b", "label": "CodeLlama 7B", "speed": "🔥 Mittel", "desc": "Meta – Code-Spezialist", "vision": False},
    {"name": "codellama:13b", "label": "CodeLlama 13B", "speed": "🔥 Mittel", "desc": "Meta – Code-Experte", "vision": False},
    {"name": "nomic-embed-text", "label": "Nomic Embed", "speed": "⚡ Ultra", "desc": "Embeddings-Modell", "vision": False},
    {"name": "llava", "label": "LLaVA 7B", "speed": "🔥 Mittel", "desc": "🎥 Vision – Bild + Text", "vision": True},
    {"name": "llava:13b", "label": "LLaVA 13B", "speed": "🧠 Langsam", "desc": "🎥 Vision – stärker", "vision": True},
    {"name": "llava-phi3", "label": "LLaVA-Phi3", "speed": "⚡ Schnell", "desc": "🎥 Vision – kompakt", "vision": True},
    {"name": "moondream", "label": "Moondream 2", "speed": "⚡ Sehr schnell", "desc": "🎥 Vision – ultra-klein", "vision": True},
    {"name": "minicpm-v", "label": "MiniCPM-V", "speed": "🔥 Mittel", "desc": "🎥 Vision – gut & schnell", "vision": True},
    {"name": "llava-llama3", "label": "LLaVA-Llama3", "speed": "🧠 Langsam", "desc": "🎥 Vision – sehr stark", "vision": True},
]

TEMPLATE_FOLDER = _TEMPLATE_FOLDER


def get_secret_key() -> str:
    secret_from_env = os.getenv("SECRET_KEY")
    if secret_from_env:
        return secret_from_env

    secret_dir = DATA_DIR
    os.makedirs(secret_dir, exist_ok=True)
    secret_path = os.path.join(secret_dir, ".secret_key")
    try:
        if os.path.exists(secret_path):
            return open(secret_path, "r", encoding="utf-8").read().strip()
        key = os.urandom(32).hex()
        with open(secret_path, "w", encoding="utf-8") as f:
            f.write(key)
        try:
            os.chmod(secret_path, 0o600)
        except OSError:
            pass
        return key
    except OSError:
        return os.urandom(32).hex()
