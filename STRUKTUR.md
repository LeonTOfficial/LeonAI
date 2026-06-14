# LEON AI Architecture

![Architecture](https://img.shields.io/badge/architecture-modular-5357ff?style=for-the-badge)
![Backend](https://img.shields.io/badge/backend-Flask-111827?style=for-the-badge)
![Frontend](https://img.shields.io/badge/frontend-vanilla%20JS-17a673?style=for-the-badge)
![Database](https://img.shields.io/badge/database-SQLite-d99b18?style=for-the-badge)

### What This Document Explains

This document is an architectural overview of LEON AI. It is not a step-by-step manual. It explains how the project is organized, which folder owns which responsibility, how data moves through the app, and where logs, errors, and local runtime data live.

LEON AI is a modular local web application built with Flask, SQLite, Ollama, and Vanilla JavaScript. It is designed to run locally on macOS, Windows, and Linux as long as Python, the dependencies, and Ollama are available.

### Architecture In One Sentence

The backend is split into routes, services, models, and utilities; the frontend is split into small JavaScript modules; SQLite stores local state; Ollama provides local model inference; and the browser renders chat, artifacts, charts, diagrams, and dashboard views.

### Folder Overview

```text
Leon-ai/
├── app.py                     # Flask entry point and local server bootstrap
├── config.py                  # central paths, models, prompts, auth, limits
├── requirements.txt           # Python dependencies for the backend
├── Starten.command            # macOS launcher with local status output
├── .env.example               # safe template for local environment values
├── .gitignore                 # keeps secrets, databases, logs, backups out of Git
├── README.md                  # public project overview and installation
├── SECURITY.md                # security model and vulnerability reporting
├── STRUKTUR.md                # this architecture overview
├── TESTING.md                 # automated tests, manual QA, release checks
├── CHANGELOG.md               # public release history
├── UPDATES.md                 # internal developer log and debugging notes
├── LICENSE                    # license terms
├── .github/
│   └── workflows/
│       └── test.yml           # GitHub Actions CI for tests and JS syntax
├── docs/
│   └── screenshots/           # README screenshots and public visuals
├── models/
│   ├── __init__.py            # package marker
│   └── database.py            # SQLite schema, migrations, connection helper
├── routes/
│   ├── __init__.py            # blueprint registration
│   ├── api.py                 # JSON endpoints for rooms, stats, privacy, artifacts
│   ├── auth.py                # login, logout, first setup, profile setup
│   ├── chat.py                # streaming chat, vision, model actions
│   ├── middleware.py          # request IDs, CSRF/origin checks, security headers
│   └── pages.py               # HTML pages, dashboard, app shell, PWA files
├── services/
│   ├── __init__.py            # package marker
│   ├── artifact_service.py    # artifact versions, dedupe, preview history
│   ├── backup_service.py      # SQLite backups and integrity metadata
│   ├── chat_service.py        # context building, token estimates, branching, titles
│   ├── export_service.py      # readable chat exports
│   ├── memory_service.py      # saved memory and automatic memory entries
│   ├── ollama_service.py      # local Ollama API and model discovery
│   ├── profile_service.py     # first setup, user profile, migration helpers
│   └── room_service.py        # chat rooms, pinning, empty-room cleanup
├── static/
│   └── js/
│       ├── api.js             # shared state, fetch helper, CSRF headers
│       ├── artifacts.js       # iframe preview, Pyodide, terminal/error bridge
│       ├── chat.js            # messages, streaming, Markdown, colors, charts
│       └── ui.js              # sidebar, modals, theme, settings, dashboard links
├── templates/
│   ├── dashboard.html         # dashboard UI, charts, privacy/debug panels
│   └── index.html             # login, setup, chat shell, artifact panel markup
├── tests/
│   ├── test_core.py           # backend, security, database, service tests
│   └── test_ui_flows.py       # frontend contracts and user-flow expectations
├── utils/
│   ├── __init__.py            # package marker
│   ├── debug_logs.py          # debug-center helpers
│   ├── errors.py              # safe error responses and log shielding
│   ├── logging.py             # structured logs and terminal activity lines
│   ├── media.py               # upload/media helpers
│   ├── privacy.py             # local data summary and cleanup tools
│   ├── security.py            # auth, CSRF, origin, rate-limit helpers
│   ├── system_health.py       # health checks for DB, logs, backups, Ollama
│   └── text.py                # text cleanup and sanitization helpers
├── data/                      # local runtime data, not part of the repository
├── backup/                    # local backups, not part of the repository
└── venv/                      # local Python environment, not part of the repository
```

### Core Files

| File | Role |
| --- | --- |
| `app.py` | Creates the Flask application, initializes the database/profile layer, registers routes, starts error handling, and launches the local server. |
| `config.py` | Central configuration for paths, host/port, model names, authentication, rate limits, uploads, and system prompts. |
| `requirements.txt` | Small Python dependency list for the local backend. |
| `Starten.command` | macOS convenience launcher. Windows and Linux use the same backend through their normal Python/terminal workflow. |

### Backend Layers

| Layer | Folder | Meaning |
| --- | --- | --- |
| Routes | `routes/` | HTTP entry points. They receive browser requests and return pages, JSON, or streaming responses. |
| Services | `services/` | Application logic. This is where chat context, artifacts, backups, exports, memory, profiles, rooms, and Ollama integration are handled. |
| Models | `models/` | SQLite connection, schema creation, and migrations. |
| Utilities | `utils/` | Shared helpers for security, logging, privacy, media handling, error handling, and health checks. |

### Route Modules

| File | Responsibility |
| --- | --- |
| `routes/auth.py` | Login, logout, first setup, password and first-name setup. |
| `routes/pages.py` | Main chat page, dashboard page, manifest, and service-worker compatibility. |
| `routes/api.py` | JSON API for rooms, messages, memory, templates, stats, privacy, health, backups, and artifacts. |
| `routes/chat.py` | Streaming chat, vision requests, model actions, and Ollama-backed generation. |
| `routes/middleware.py` | Security headers, request IDs, origin/CSRF checks, and terminal activity messages. |

### Service Modules

| File | Responsibility |
| --- | --- |
| `artifact_service.py` | Stores artifact versions, deduplicates repeated content, deletes versions, and supports preview history. |
| `backup_service.py` | Creates SQLite backups and writes integrity metadata. |
| `chat_service.py` | Builds chat context, estimates tokens, follows selected branch paths, and creates auto titles. |
| `export_service.py` | Exports chats in readable formats. |
| `memory_service.py` | Handles manually and automatically stored memory items. |
| `ollama_service.py` | Talks to Ollama, lists models, and detects vision-capable models. |
| `profile_service.py` | Stores first setup/profile information and migrates older installs. |
| `room_service.py` | Manages chat rooms, pinning, empty-room cleanup, and active room lists. |

### Database Model

SQLite keeps LEON AI simple and local. The important tables are:

| Table | Meaning |
| --- | --- |
| `rooms` | Chat workspaces, selected model, system prompt, pin/favorite metadata. |
| `messages` | Chat messages, branch parent IDs, tokens, favorites, image metadata. |
| `artifacts` | Saved generated preview versions. |
| `memory` | Saved facts and memory entries. |
| `templates` | Reusable prompt templates. |
| `snippets` | Saved code snippets. |
| `profile` | Setup status and profile information. |

### Frontend Modules

| File | Role |
| --- | --- |
| `static/js/api.js` | Shared `window.Leon` state, API helper, CSRF headers, status handling. |
| `static/js/ui.js` | Sidebar, room list, modals, theme controls, settings, dashboard navigation. |
| `static/js/chat.js` | Messages, streaming, Markdown, Mermaid diagrams, Chart.js graphs, color tags, uploads. |
| `static/js/artifacts.js` | Artifact extraction, iframe preview, Tailwind injection, Pyodide, terminal/error bridge, export controls. |

The frontend loads in this order:

```text
api.js -> ui.js -> artifacts.js -> chat.js
```

### Chat Data Flow

```text
Browser input
  -> static/js/chat.js
  -> POST /chat/stream
  -> routes/chat.py
  -> services/chat_service.py
  -> services/ollama_service.py
  -> Ollama at localhost:11434
  -> Server-Sent Events back to the browser
  -> final answer saved in SQLite
```

### Artifact Preview Flow

```text
AI response with code blocks
  -> static/js/chat.js renders the message
  -> static/js/artifacts.js extracts HTML/CSS/JS/Python
  -> iframe renders the preview
  -> console and errors are mirrored into the panel
  -> versions can be stored through services/artifact_service.py
```

### Logs And Errors

LEON AI separates user-facing errors from developer-facing details.

| Area | Explanation |
| --- | --- |
| Browser errors | The user sees a clean message and, when useful, a request ID. |
| Local logs | Detailed information is written to `data/logs/leon.log`. |
| Request IDs | A request ID connects what the browser showed with what the log recorded. |
| Terminal activity | The start terminal can show friendly activity lines such as “Chat opened” or “New chat created”. |
| Internal details | Stack traces and technical internals are kept out of normal browser responses. |

### Local Runtime Data

| Path | Meaning |
| --- | --- |
| `data/chats.db` | Local SQLite database with rooms, messages, memory, and artifacts. |
| `data/logs/leon.log` | Local runtime log with request IDs. |
| `data/.secret_key` | Generated Flask secret for local sessions. |
| `backup/` | Local SQLite backups. |

These paths are local runtime data and should not be committed.

### Platform Notes

| Platform | Notes |
| --- | --- |
| macOS | Uses `Starten.command` for a polished local start experience. |
| Windows | Uses PowerShell or Command Prompt with a Python virtual environment and `python app.py`. |
| Linux | Uses a Python virtual environment and `python app.py`; Ollama should run as a local service or process. |
