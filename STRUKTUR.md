# LEON AI Architecture

![Architecture](https://img.shields.io/badge/architecture-modular-5357ff?style=for-the-badge)
![Backend](https://img.shields.io/badge/backend-Flask-111827?style=for-the-badge)
![Frontend](https://img.shields.io/badge/frontend-vanilla%20JS-17a673?style=for-the-badge)
![Database](https://img.shields.io/badge/database-SQLite-d99b18?style=for-the-badge)

> German version below.
> Deutsche Version weiter unten.

## English Version

### What This Document Explains

This document is an architectural overview of LEON AI. It is not a step-by-step manual. It explains how the project is organized, which folder owns which responsibility, how data moves through the app, and where logs, errors, and local runtime data live.

LEON AI is a modular local web application built with Flask, SQLite, Ollama, and Vanilla JavaScript. It is designed to run locally on macOS, Windows, and Linux as long as Python, the dependencies, and Ollama are available.

### Architecture In One Sentence

The backend is split into routes, services, models, and utilities; the frontend is split into small JavaScript modules; SQLite stores local state; Ollama provides local model inference; and the browser renders chat, artifacts, charts, diagrams, and dashboard views.

### Folder Overview

```text
Leon-ai/
├── app.py
├── config.py
├── requirements.txt
├── Starten.command
├── .env.example
├── .gitignore
├── README.md
├── SECURITY.md
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
├── data/       # local runtime data, not part of the repository
├── backup/     # local backups, not part of the repository
└── venv/       # local Python environment, not part of the repository
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

## Deutsche Version

### Was dieses Dokument erklärt

Dieses Dokument ist eine Architektur-Übersicht zu LEON AI. Es ist keine reine Schritt-für-Schritt-Anleitung. Es erklärt, wie das Projekt aufgebaut ist, welcher Ordner welche Verantwortung trägt, wie Daten durch die App laufen und wo Logs, Fehler und lokale Laufzeitdaten liegen.

LEON AI ist eine modulare lokale Webanwendung mit Flask, SQLite, Ollama und Vanilla JavaScript. Die App ist so aufgebaut, dass sie lokal unter macOS, Windows und Linux laufen kann, wenn Python, die Abhängigkeiten und Ollama verfügbar sind.

### Architektur in einem Satz

Das Backend ist in Routen, Services, Models und Utilities aufgeteilt; das Frontend besteht aus kleinen JavaScript-Modulen; SQLite speichert lokale Daten; Ollama liefert lokale Modellantworten; und der Browser rendert Chat, Artifacts, Charts, Diagramme und Dashboard-Ansichten.

### Ordnerüberblick

```text
Leon-ai/
├── app.py
├── config.py
├── requirements.txt
├── Starten.command
├── .env.example
├── .gitignore
├── README.md
├── SECURITY.md
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
├── data/       # lokale Laufzeitdaten, nicht Teil des Repositorys
├── backup/     # lokale Backups, nicht Teil des Repositorys
└── venv/       # lokale Python-Umgebung, nicht Teil des Repositorys
```

### Kerndateien

| Datei | Rolle |
| --- | --- |
| `app.py` | Erstellt die Flask-App, initialisiert Datenbank/Profile, registriert Routen, startet Fehlerbehandlung und lokalen Server. |
| `config.py` | Zentrale Konfiguration für Pfade, Host/Port, Modellnamen, Authentifizierung, Rate Limits, Uploads und System-Prompts. |
| `requirements.txt` | Kleine Python-Abhängigkeitsliste für das lokale Backend. |
| `Starten.command` | Komfortabler macOS-Starter. Windows und Linux nutzen dasselbe Backend über ihren normalen Python-/Terminal-Weg. |

### Backend-Schichten

| Schicht | Ordner | Bedeutung |
| --- | --- | --- |
| Routen | `routes/` | HTTP-Einstiegspunkte. Sie nehmen Browser-Anfragen an und liefern Seiten, JSON oder Streaming-Antworten zurück. |
| Services | `services/` | Fachlogik. Hier liegen Chat-Kontext, Artifacts, Backups, Exporte, Memory, Profile, Räume und Ollama-Anbindung. |
| Models | `models/` | SQLite-Verbindung, Schema-Erstellung und Migrationen. |
| Utilities | `utils/` | Gemeinsame Helfer für Sicherheit, Logging, Datenschutz, Medien, Fehlerbehandlung und Health Checks. |

### Routenmodule

| Datei | Verantwortung |
| --- | --- |
| `routes/auth.py` | Login, Logout, First Setup, Passwort und Vorname. |
| `routes/pages.py` | Chat-Hauptseite, Dashboard, Manifest und Service-Worker-Kompatibilität. |
| `routes/api.py` | JSON-API für Räume, Nachrichten, Memory, Templates, Statistiken, Datenschutz, Health, Backups und Artifacts. |
| `routes/chat.py` | Streaming-Chat, Vision-Anfragen, Modellaktionen und Ollama-generierte Antworten. |
| `routes/middleware.py` | Security Header, Request-IDs, Origin-/CSRF-Prüfung und Terminal-Aktivitätsmeldungen. |

### Servicemodule

| Datei | Verantwortung |
| --- | --- |
| `artifact_service.py` | Speichert Artifact-Versionen, dedupliziert wiederholte Inhalte, löscht Versionen und unterstützt den Vorschau-Verlauf. |
| `backup_service.py` | Erstellt SQLite-Backups und schreibt Integritätsmetadaten. |
| `chat_service.py` | Baut Chat-Kontext, schätzt Tokens, folgt ausgewählten Branches und erzeugt Auto-Titel. |
| `export_service.py` | Exportiert Chats in lesbaren Formaten. |
| `memory_service.py` | Verwaltet manuelle und automatisch gespeicherte Memory-Einträge. |
| `ollama_service.py` | Spricht mit Ollama, listet Modelle und erkennt Vision-fähige Modelle. |
| `profile_service.py` | Speichert First-Setup-/Profildaten und migriert ältere Installationen. |
| `room_service.py` | Verwaltet Chat-Räume, Anpinnen, Aufräumen leerer Räume und aktive Raumlisten. |

### Datenbankmodell

SQLite hält LEON AI einfach und lokal. Die wichtigsten Tabellen sind:

| Tabelle | Bedeutung |
| --- | --- |
| `rooms` | Chat-Arbeitsbereiche, ausgewähltes Modell, System-Prompt, Pin-/Favoriten-Metadaten. |
| `messages` | Chat-Nachrichten, Branch-Parent-IDs, Tokens, Favoriten, Bildmetadaten. |
| `artifacts` | Gespeicherte Vorschau-Versionen. |
| `memory` | Gespeicherte Fakten und Memory-Einträge. |
| `templates` | Wiederverwendbare Prompt-Vorlagen. |
| `snippets` | Gespeicherte Code-Snippets. |
| `profile` | Setup-Status und Profilinformationen. |

### Frontend-Module

| Datei | Rolle |
| --- | --- |
| `static/js/api.js` | Gemeinsamer `window.Leon`-State, API-Helfer, CSRF-Header und Statusbehandlung. |
| `static/js/ui.js` | Sidebar, Raumliste, Modals, Theme-Steuerung, Einstellungen und Dashboard-Navigation. |
| `static/js/chat.js` | Nachrichten, Streaming, Markdown, Mermaid-Diagramme, Chart.js-Grafiken, Farbtags und Uploads. |
| `static/js/artifacts.js` | Artifact-Erkennung, iframe-Vorschau, Tailwind-Injection, Pyodide, Terminal-/Fehlerbrücke und Exportsteuerung. |

Das Frontend lädt in dieser Reihenfolge:

```text
api.js -> ui.js -> artifacts.js -> chat.js
```

### Datenfluss im Chat

```text
Browser-Eingabe
  -> static/js/chat.js
  -> POST /chat/stream
  -> routes/chat.py
  -> services/chat_service.py
  -> services/ollama_service.py
  -> Ollama auf localhost:11434
  -> Server-Sent Events zurück zum Browser
  -> finale Antwort wird in SQLite gespeichert
```

### Datenfluss in der Artifact-Vorschau

```text
KI-Antwort mit Codeblöcken
  -> static/js/chat.js rendert die Nachricht
  -> static/js/artifacts.js extrahiert HTML/CSS/JS/Python
  -> iframe rendert die Vorschau
  -> Konsole und Fehler werden ins Panel gespiegelt
  -> Versionen können über services/artifact_service.py gespeichert werden
```

### Logs und Fehler

LEON AI trennt sichtbare Nutzerfehler von technischen Details für Entwickler.

| Bereich | Erklärung |
| --- | --- |
| Browser-Fehler | Der Nutzer sieht eine klare Meldung und, wenn sinnvoll, eine Request-ID. |
| Lokale Logs | Detaillierte Informationen werden in `data/logs/leon.log` geschrieben. |
| Request-IDs | Eine Request-ID verbindet die Browser-Meldung mit dem passenden Log-Eintrag. |
| Terminal-Aktivität | Das Start-Terminal kann freundliche Aktivitätszeilen wie „Chat geöffnet“ oder „Neuer Chat erstellt“ anzeigen. |
| Interne Details | Stacktraces und technische Interna bleiben aus normalen Browser-Antworten heraus. |

### Lokale Laufzeitdaten

| Pfad | Bedeutung |
| --- | --- |
| `data/chats.db` | Lokale SQLite-Datenbank mit Räumen, Nachrichten, Memory und Artifacts. |
| `data/logs/leon.log` | Lokales Laufzeitlog mit Request-IDs. |
| `data/.secret_key` | Generiertes Flask-Secret für lokale Sessions. |
| `backup/` | Lokale SQLite-Backups. |

Diese Pfade sind lokale Laufzeitdaten und sollten nicht committed werden.

### Plattform-Hinweise

| Plattform | Hinweise |
| --- | --- |
| macOS | Nutzt `Starten.command` für einen komfortablen lokalen Start. |
| Windows | Nutzt PowerShell oder Eingabeaufforderung mit Python-Umgebung und `python app.py`. |
| Linux | Nutzt Python-Umgebung und `python app.py`; Ollama sollte als lokaler Dienst oder Prozess laufen. |
