# LEON AI - Struktur und Architektur

Stand: Juni 2026

LEON AI ist eine lokale Flask-Webapp fuer macOS. Die App verbindet einen privaten Chat-Arbeitsbereich mit Ollama, SQLite, Live-Artifacts, Diagrammen, Python-Vorschau und Dashboard/Privacy-Werkzeugen.

## Architektur in einem Satz

Backend und Frontend sind modular getrennt: Flask-Routen nehmen HTTP-Anfragen an, Services enthalten die Fachlogik, Models verwalten SQLite, Utils buendeln Sicherheit/Logging/Fehler, und das Frontend liegt in kleinen JavaScript-Modulen unter `static/js/`.

## Echte Ordnerstruktur

```text
Leon-ai/
├── app.py
├── config.py
├── requirements.txt
├── Starten.command
├── .env.example
├── .gitignore
├── README.md
├── README_SICHERHEIT.txt
├── STRUKTUR.md
├── TESTING.md
├── LICENSE
├── docs/
│   └── screenshots/
├── models/
│   ├── __init__.py
│   └── database.py
├── routes/
│   ├── __init__.py
│   ├── api.py
│   ├── auth.py
│   ├── chat.py
│   ├── middleware.py
│   └── pages.py
├── services/
│   ├── __init__.py
│   ├── artifact_service.py
│   ├── backup_service.py
│   ├── chat_service.py
│   ├── export_service.py
│   ├── memory_service.py
│   ├── ollama_service.py
│   ├── profile_service.py
│   └── room_service.py
├── static/
│   └── js/
│       ├── api.js
│       ├── artifacts.js
│       ├── chat.js
│       └── ui.js
├── templates/
│   ├── dashboard.html
│   └── index.html
├── tests/
│   ├── test_core.py
│   └── test_ui_flows.py
├── utils/
│   ├── __init__.py
│   ├── debug_logs.py
│   ├── errors.py
│   ├── logging.py
│   ├── media.py
│   ├── privacy.py
│   ├── security.py
│   ├── system_health.py
│   └── text.py
├── data/       # lokal, nicht ins Repository
├── backup/     # lokal, nicht ins Repository
└── venv/       # lokal, nicht ins Repository
```

## Startpunkt

| Datei | Aufgabe |
| --- | --- |
| `Starten.command` | macOS-Startskript. Setzt Port/Host, prueft venv, installiert Abhaengigkeiten und startet `app.py`. Terminalausgabe ist bewusst minimal. |
| `app.py` | Erstellt die Flask-App, initialisiert DB, Profile, Routes, Error Handler und Backup-Thread. |
| `config.py` | Zentrale Konfiguration: Pfade, Modelle, Host/Port, Auth, Rate Limit, Uploads und System-Prompts. |

## Backend-Module

### `routes/`

| Datei | Aufgabe |
| --- | --- |
| `routes/auth.py` | Login, Logout, First Setup, Passwort/Name speichern. |
| `routes/pages.py` | Hauptseite, Dashboard, Manifest, Service-Worker-Kompatibilitaet. |
| `routes/api.py` | REST-API fuer Raeume, Nachrichten, Memory, Templates, Stats, Privacy, Health, Artifacts. |
| `routes/chat.py` | Streaming-Endpunkte fuer normale Chats, Vision und Modellaktionen. |
| `routes/middleware.py` | Security Header, Request-ID, CSRF-/Origin-Gate, Aktivitaetslogging. |

### `services/`

| Datei | Aufgabe |
| --- | --- |
| `artifact_service.py` | Persistente Artifact-Versionen in SQLite, Dedupe und Loeschen. |
| `backup_service.py` | SQLite-Backup, Manifest und Integritaetspruefung. |
| `chat_service.py` | Chat-Kontext, Token-Schaetzung, Branching-Pfade, Auto-Titel. |
| `export_service.py` | Export von Chats als Text/Markdown/HTML/JSON. |
| `memory_service.py` | Automatische und manuelle Memory-Eintraege. |
| `ollama_service.py` | Ollama-Verbindung, Modellliste, Vision-Modell-Erkennung. |
| `profile_service.py` | Profil/First-Setup-Daten und Migration bestehender Installationen. |
| `room_service.py` | Raeume, leere Chats aufraeumen, aktive Chatlisten. |

### `models/`

| Datei | Aufgabe |
| --- | --- |
| `models/database.py` | SQLite-Verbindung, Tabellen, Migrationen und Schema-Erweiterungen. |

Wichtige Tabellen:

- `rooms`: Chat-Raeume, Modell, System-Prompt, Pin/Favorit/Meta.
- `messages`: Chat-Nachrichten, Parent-ID fuer Branching, Token, Favorit, Bildpfad.
- `artifacts`: gespeicherte Vorschau-Versionen.
- `memory`: gespeicherte Fakten.
- `templates`: Prompt-Vorlagen.
- `snippets`: Code-Snippets.
- `profile`: Name und Setup-Status.

### `utils/`

| Datei | Aufgabe |
| --- | --- |
| `security.py` | Login-Pflicht, Passwortpruefung, CSRF, Origin-Check, Rate-Limit-Helfer. |
| `errors.py` | Zentraler Fehlerhandler mit Request-ID und ohne interne Details im Browser. |
| `logging.py` | Rotierende Datei-Logs, Request-Kontext, ruhiges Terminal. |
| `privacy.py` | Datenzaehlung und geschuetztes Loeschen privater Bereiche. |
| `system_health.py` | Health Checks fuer DB, Logs, Backups und Ollama. |
| `debug_logs.py` | Debug-Center-Daten fuer das Dashboard. |
| `media.py` | Upload-/Medien-Helfer. |
| `text.py` | Eingabebereinigung, Namen/Modelle validieren. |

## Frontend-Module

| Datei | Aufgabe |
| --- | --- |
| `static/js/api.js` | Globaler `window.Leon`-State, API-Wrapper, CSRF-Header, Status. |
| `static/js/ui.js` | Sidebar, Settings, Theme, Room-Liste, Modals, Dashboard-Navigation. |
| `static/js/chat.js` | Nachrichten, Streaming, Markdown, Mermaid, Chart.js, Farbtags, Uploads. |
| `static/js/artifacts.js` | Live-Vorschau, HTML/CSS/JS, Tailwind-Injection, Pyodide, Terminal/Fehler-Panel, ZIP/HTML-Export. |

Lade-Reihenfolge in `templates/index.html`:

```text
api.js -> ui.js -> artifacts.js -> chat.js
```

## Datenfluss Chat

```text
Browser
  -> static/js/chat.js
  -> POST /chat/stream
  -> routes/chat.py
  -> services/chat_service.py
  -> services/ollama_service.py
  -> Ollama localhost:11434
  -> SSE-Stream zurueck zum Browser
  -> Antwort in SQLite speichern
```

## Datenfluss Artifact-Vorschau

```text
KI-Antwort mit Codeblock
  -> static/js/chat.js rendert Nachricht
  -> static/js/artifacts.js extrahiert HTML/CSS/JS/Python
  -> Vorschau iframe rendert srcdoc
  -> Terminal/Fehler werden per postMessage ins Panel gespiegelt
  -> Version kann ueber services/artifact_service.py gespeichert werden
```

## Sicherheit im Aufbau

| Ebene | Schutz |
| --- | --- |
| Netzwerk | `HOST=127.0.0.1` als Standard. |
| Auth | Login/First Setup in `routes/auth.py`. |
| Browser-Requests | CSRF und Origin-Check in `utils/security.py` + `routes/middleware.py`. |
| Fehler | Request-ID statt interner Details in `utils/errors.py`. |
| HTML-Ausgabe | DOMPurify/Renderer-Vertraege in `static/js/chat.js`. |
| Vorschau | iframe-Isolation und Asset-Neutralisierung in `static/js/artifacts.js`. |
| GitHub | `.gitignore` blockiert lokale Daten, Logs, Backups, Secrets und venv. |

Mehr Details: `README_SICHERHEIT.txt`

## Lokale Daten

| Pfad | Bedeutung |
| --- | --- |
| `data/chats.db` | SQLite-Datenbank mit Chats, Raeumen, Nachrichten, Memory und Artifacts. |
| `data/logs/leon.log` | Laufzeitlog mit Request-IDs. Bei Fehlern zuerst hier nachsehen. |
| `data/.secret_key` | Automatisch generierter Flask-Secret-Key. |
| `backup/` | Lokale SQLite-Backups. |

Diese Ordner sind lokal und gehoeren nicht ins Repository.

## Konfiguration

Wichtige `.env`-Variablen:

| Variable | Standard | Bedeutung |
| --- | --- | --- |
| `PORT` | `5001` | Webserver-Port. |
| `HOST` | `127.0.0.1` | Nur lokaler Mac. |
| `LEON_PASSWORD` | Fallback | Passwort fuer bestehende Installationen. |
| `AUTH_ENABLED` | `true` | Login aktivieren/deaktivieren. |
| `OLLAMA_BASE` | `http://localhost:11434` | Ollama-Endpunkt. |
| `OLLAMA_MODEL` | `llama3` | Standardmodell. |
| `RATE_LIMIT_REQUESTS` | `30` | Max. Requests pro Fenster. |
| `LEON_TERMINAL_ACTIVITY` | `0` | Terminal-Aktivitaetsstream einschalten, wenn gewuenscht. |
| `LEON_TERMINAL_LOG_LEVEL` | `CRITICAL` | Console-Log-Level; Details bleiben in `data/logs/leon.log`. |
| `LEON_STARTUP_VERBOSE` | `0` | Ausfuehrliche Startanzeige einschalten. |

## Debugging

Terminal bleibt absichtlich ruhig. Details stehen hier:

```bash
tail -n 80 data/logs/leon.log
grep -E "ERROR|WARNING" data/logs/leon.log
```

Bei einem Browserfehler mit Request-ID:

```bash
grep "REQUEST_ID_HIER" data/logs/leon.log
```

## Tests

```bash
./venv/bin/python -m unittest discover -s tests -q
node --check static/js/api.js
node --check static/js/ui.js
node --check static/js/artifacts.js
node --check static/js/chat.js
```

Mehr Details: `TESTING.md`
