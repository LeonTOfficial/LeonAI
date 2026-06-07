# LEON AI – Projektbriefing & Struktur

> Kurzüberblick für alle, die am Projekt mitarbeiten oder es erweitern wollen.
> Stand: Juni 2026 · Version 4 (modular)

---

## Was ist LEON AI?

LEON AI ist ein **lokales KI-Interface** auf dem Mac. Es verbindet sich mit **Ollama** (localhost:11434), speichert Chats in **SQLite** und läuft als **Flask-Webapp** auf Port **5001**.

---

## Ordnerstruktur (Übersicht)

```
Leon-ai/
│
├── app.py                  ← Startpunkt: App starten, Server booten
├── config.py               ← Alle Einstellungen (Port, Passwort, Ollama, Modelle)
├── requirements.txt        ← Python-Abhängigkeiten
├── Starten.command         ← Doppelklick-Start für macOS
│
├── STRUKTUR.md             ← Dieses Briefing (+ Log-Auswertungs-Anleitung)
├── UPDATES.md              ← Änderungsprotokoll (was wann gemacht wurde)
├── START_HIER.txt          ← Schnellstart-Anleitung
│
├── data/logs/leon.log      ← LAUFZEIT-LOG – bei Fehlern zuerst hier schauen!
│
├── models/                 ← DATENBANK-SCHEMATA
├── services/               ← GESCHÄFTSLOGIK (Ollama, Chat, Memory, Export …)
├── routes/                 ← API-ENDPUNKTE & SEITEN
├── utils/                  ← HILFSFUNKTIONEN (Logging, Security, Fehler)
│
├── templates/              ← HTML-Seiten (index.html, dashboard.html)
├── static/js/              ← Frontend-JavaScript (modular)
│
├── data/                   ← Laufzeitdaten (DB, Logs, Secret Key) – nicht löschen!
└── backup/                 ← Automatische DB-Backups (max. 7 Tage)
```

---

## Backend – Was macht welche Datei?

### Einstieg

| Datei | Aufgabe |
|-------|---------|
| `app.py` | Erstellt die Flask-App, startet den Server. Hier nichts Komplexes einbauen – nur bootstrappen. |
| `config.py` | Zentrale Konfiguration: `PORT`, `OLLAMA_BASE`, `AUTH_ENABLED`, Modell-Listen, Pfade. Alles über `.env` überschreibbar. |

### `/models` – Datenbank

| Datei | Aufgabe |
|-------|---------|
| `database.py` | SQLite-Schema (rooms, messages, memory, templates, snippets), `init_db()`, `get_db()`. Migrationen für neue Spalten laufen hier. |

**Tabellen:**
- `rooms` – Chat-Räume (Name, Modell, System-Prompt, Pin …)
- `messages` – Nachrichten (user/ai, Tokens, Favorit, Bild …)
- `memory` – Gespeicherte Fakten pro Raum
- `templates` – Wiederverwendbare Prompt-Vorlagen
- `snippets` – Code-Snippets

### `/services` – Logik (kein HTTP hier)

| Datei | Aufgabe |
|-------|---------|
| `ollama_service.py` | Ollama erreichbar? Modell-Liste, Vision-Modell auswählen |
| `chat_service.py` | Kontext aufbauen, Token-Schätzung, Nachrichten-Historie |
| `memory_service.py` | Automatische Erinnerungen aus User-Nachrichten |
| `backup_service.py` | Tägliches DB-Backup nach `backup/` |
| `export_service.py` | Chat-Export als TXT, MD, HTML, JSON |

### `/routes` – HTTP-Endpunkte

| Datei | Aufgabe |
|-------|---------|
| `auth.py` | `/login`, `/logout` – Passwort-Authentifizierung |
| `pages.py` | `/`, `/dashboard`, PWA (`manifest.json`, `sw.js`) |
| `api.py` | REST-API unter `/api/*` (Rooms, Messages, Templates, Stats, Vision …) |
| `chat.py` | SSE-Streaming: `/chat/stream`, `/chat/vision/stream`, `/api/pull` |
| `middleware.py` | Security-Headers, Request-Logging, Origin-Check |

### `/utils` – Querschnitt

| Datei | Aufgabe |
|-------|---------|
| `logging.py` | Strukturiertes Logging → `data/logs/leon.log` (+ Terminal-Aktivität) |
| `security.py` | Login-Decorator, Rate-Limiting, Passwort-Hash, Origin-Prüfung |
| `text.py` | Input-Bereinigung (`clean_text`, `clean_name`, Modellname-Validierung) |
| `errors.py` | Zentraler Fehler-Handler (HTTP + unerwartete Exceptions) |

---

## Frontend – Was macht welche Datei?

Die Logik steckt nicht mehr in `index.html`, sondern in **`static/js/`**:

| Datei | Aufgabe |
|-------|---------|
| `api.js` | Globaler State (`Leon.state`), Fetch-Wrapper `Leon.api()`, Status-Check |
| `ui.js` | Theme, Modals, Sidebar, Einstellungen, Raumliste, Vorlagen, Suche |
| `artifacts.js` | Live-Vorschau-Panel für HTML/CSS/JS aus KI-Antworten |
| `chat.js` | Nachrichten senden, SSE-Streaming, Bild-Upload, App-Init |

Alle Module hängen am Namespace **`window.Leon`**. HTML-`onclick`-Handler rufen weiter globale Funktionen auf (`sendMessage()`, `openSettings()` …).

**Lade-Reihenfolge in `index.html`:**
```
api.js → ui.js → artifacts.js → chat.js
```

---

## Datenfluss (vereinfacht)

```
Browser (index.html + static/js/)
    │
    ├── GET/POST  /api/*        → routes/api.py      → models/database.py
    ├── POST      /chat/stream  → routes/chat.py     → services/chat_service.py
    │                                              → services/ollama_service.py → Ollama
    └── GET       /login        → routes/auth.py     → utils/security.py
```

**Streaming-Ablauf (Chat):**
1. User sendet Nachricht → `chat.js` → `POST /chat/stream`
2. Route speichert User-Nachricht in SQLite
3. `chat_service.build_messages()` baut Kontext (Historie + Memory + System-Prompt)
4. Ollama antwortet per SSE (Token für Token)
5. AI-Antwort wird am Ende in SQLite gespeichert
6. Frontend rendert live mit `updateTempMessage()`

---

## Wichtige Pfade & Dateien

| Pfad | Inhalt |
|------|--------|
| `data/chats.db` | SQLite-Datenbank mit allen Chats |
| `data/logs/leon.log` | Fehler- und Ereignis-Log (bei Problemen zuerst hier schauen) |
| `data/.secret_key` | Session-Secret (automatisch generiert) |
| `data/Persönliche_Akte.txt` | Manuell/automatisch gespeicherte Fakten |
| `backup/chats_YYYY-MM-DD.db` | Tägliche DB-Backups |

---

## Konfiguration (.env)

Kopiere `.env.example` nach `.env` und passe an:

| Variable | Standard | Bedeutung |
|----------|----------|-----------|
| `PORT` | `5001` | Webserver-Port |
| `HOST` | `127.0.0.1` | Nur lokal (0.0.0.0 = Netzwerk) |
| `LEON_PASSWORD` | `leon2026` | Login-Passwort |
| `AUTH_ENABLED` | `true` | Login an/aus |
| `OLLAMA_BASE` | `http://localhost:11434` | Ollama-URL |
| `OLLAMA_MODEL` | `llama3` | Standard-Modell |
| `RATE_LIMIT` | `30` | Max. Anfragen pro Minute pro IP |

---

## Wo füge ich Neues ein?

| Ich will … | Dann hier … |
|------------|-------------|
| Neuen API-Endpunkt | `routes/api.py` (oder neue Route-Datei + in `routes/__init__.py` registrieren) |
| Streaming-Endpunkt | `routes/chat.py` |
| Ollama-/KI-Logik | `services/` (neue Service-Datei) |
| DB-Tabelle/Spalte | `models/database.py` (Migration in `migrations`-Liste) |
| Frontend-Feature | passende Datei in `static/js/` |
| Neue Einstellung | `config.py` + optional `.env.example` |
| Fehler besser loggen | `utils/logging.py` / `utils/errors.py` |

---

## Start & Debug

```bash
cd Leon-ai
source venv/bin/activate   # falls venv vorhanden
python app.py
# → http://localhost:5001
```

**Bei Fehlern – immer zuerst hier schauen:**
1. **`data/logs/leon.log`** öffnen und auswerten (siehe Abschnitt unten)
2. Terminal-Ausgabe beim Start prüfen (Ollama online?)
3. Browser: Cmd + Shift + R (Hard-Reload)

---

## Log-Datei auswerten (`data/logs/leon.log`)

> **Wichtig:** Wenn etwas nicht funktioniert, **immer zuerst `leon.log` lesen**.
> Dort steht genau, was passiert ist – mit Zeitstempel, Modul und Fehlertext.
> Fehler identifizieren → Ursache verstehen → im Code beheben → in `UPDATES.md` dokumentieren.

### Log-Datei öffnen

```bash
# Im Terminal (live mitverfolgen):
tail -f data/logs/leon.log

# Letzte 50 Zeilen:
tail -n 50 data/logs/leon.log

# Nur Fehler und Warnungen:
grep -E 'ERROR|WARNING' data/logs/leon.log
```

Oder die Datei direkt in Cursor/VS Code öffnen: `data/logs/leon.log`

### Log-Zeilen verstehen

Jede Zeile folgt diesem Format:

```
2026-06-04 15:12:26 | WARNING  | leon.errors | handle_http_exception:24 | HTTP 404 | path=/favicon.ico | ...
│                     │          │             │                          │
Datum + Uhrzeit       Level      Modul         Funktion:Zeile             Nachricht
```

| Level | Bedeutung | Was tun? |
|-------|-----------|----------|
| `INFO` | Normaler Betrieb (Start, Login, Chat, Export …) | Nichts – alles OK |
| `WARNING` | Auffälligkeit (404, falsches Passwort, Ollama langsam …) | Prüfen, ggf. beheben |
| `ERROR` | Echter Fehler (Crash, DB-Problem, Ollama-Timeout …) | **Sofort beheben** |

| Modul | Wo im Code |
|-------|------------|
| `leon` | `app.py` – App-Start |
| `leon.activity` | `routes/middleware.py` – Nutzer-Aktionen |
| `leon.errors` | `utils/errors.py` – HTTP- und Server-Fehler |
| `leon.api` | `routes/api.py` – REST-API-Fehler |
| `leon.chat` | `routes/chat.py` – Streaming-Fehler |
| `leon.backup` | `services/backup_service.py` – DB-Backup |
| `leon.ollama` | `services/ollama_service.py` – Ollama-Verbindung |

### Typische Log-Meldungen

| Meldung | Bedeutung | Aktion |
|---------|-----------|--------|
| `LEON AI App initialisiert` | App startet normal | ✅ OK |
| `Backup erstellt` | Tägliches DB-Backup erfolgreich | ✅ OK |
| `Login erfolgreich` | Anmeldung geklappt | ✅ OK |
| `Login fehlgeschlagen` | Falsches Passwort eingegeben | ⚠️ Normal bei Tippfehler; bei Wiederholung Passwort prüfen |
| `Chat lädt` / `Nachricht` | Normaler Chat-Betrieb | ✅ OK |
| `HTTP 404 \| path=/favicon.ico` | Browser sucht Icon (harmlos) | ✅ Behoben – Route existiert jetzt |
| `HTTP 404 \| path=/leon-ai-profile.jpg` | KI-Antwort enthielt relativen Bildpfad | ✅ Behoben – Frontend blockiert solche Requests |
| `HTTP 503 \| Ollama offline` | Ollama läuft nicht | ❌ `ollama serve` starten |
| `Unhandled exception` | Unerwarteter Python-Crash | ❌ Stacktrace in Log lesen, Code fixen |
| `Chat-Stream Fehler` | Verbindung zu Ollama abgebrochen | ❌ Ollama prüfen, Modell installiert? |

### Fehler beheben – Workflow

```
1. leon.log öffnen
2. Neueste ERROR/WARNING-Zeilen finden (unten in der Datei)
3. Modul + Pfad + Nachricht lesen
4. Betroffene Datei öffnen (siehe Modul-Tabelle oben)
5. Fix implementieren
6. App neu starten und testen
7. Eintrag in UPDATES.md schreiben
```

### Beispiel-Auswertung (2026-06-04)

**Ergebnis der ersten Log-Analyse:**

| Status | Anzahl | Details |
|--------|--------|---------|
| ✅ OK | ~20 | App-Start, Login, Chat, Export, Dashboard – alles normal |
| ⚠️ Behoben | ~40 | 404 für `/leon-ai-profile.jpg`, `/leon-ai-gif.gif` – kam aus KI-Antworten mit `<img src="...">` ohne echte Datei |
| ⚠️ Behoben | ~10 | 404 für `/favicon.ico`, `/apple-touch-icon.png` – Browser-Anfragen ohne Route |
| ⚠️ Harmlos | 1 | `Login fehlgeschlagen` – einmal falsches Passwort |

**Durchgeführte Fixes:**
- `routes/pages.py` – `/favicon.ico` und Apple-Touch-Icon-Routen hinzugefügt
- `static/js/chat.js` – relative Bildpfade aus KI-Antworten werden nicht mehr geladen
- `utils/errors.py` – harmlose 404-Meldungen werden nicht mehr als WARNING geloggt

---

## Weitere Dokumentation

- `START_HIER.txt` – Schnellstart
- `UPDATES.md` – Änderungsprotokoll
- `data/logs/leon.log` – **Laufzeit-Log (bei Problemen zuerst hier!)**
- `README_SICHERHEIT.txt` – Auth, Rate-Limit, CSP
- `README_FEINSCHLIFF.txt` – UI-Details