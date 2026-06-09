# LEON AI Testing

![Tests](https://img.shields.io/badge/tests-46%20automated-17a673?style=for-the-badge)
![Backend](https://img.shields.io/badge/backend-Flask-111827?style=for-the-badge)
![Frontend](https://img.shields.io/badge/frontend-vanilla%20JS-5357ff?style=for-the-badge)
![QA](https://img.shields.io/badge/QA-release%20checklist-d99b18?style=for-the-badge)

> German version below.
> Deutsche Version weiter unten.

## English Version

### 1. Quick Test Commands

Run the full automated test suite:

```bash
./venv/bin/python -m unittest discover -s tests -q
```

Run the same suite with detailed output:

```bash
./venv/bin/python -m unittest discover -s tests -v
```

Check frontend JavaScript syntax:

```bash
node --check static/js/api.js
node --check static/js/ui.js
node --check static/js/artifacts.js
node --check static/js/chat.js
```

Check for whitespace/patch problems before committing:

```bash
git diff --check
```

### 2. Current Automated Coverage

The current automated suite covers **46 tests** across backend behavior, frontend contracts, security controls, artifacts, privacy tooling, backups, and UI flow expectations.

| Test area | What is checked | Main evidence |
| --- | --- | --- |
| Database migrations | Parent IDs, artifact version tables, schema compatibility | `tests/test_core.py`, `models/database.py` |
| Authentication | Login, protected pages, first setup, session state | `tests/test_core.py`, `tests/test_ui_flows.py`, `routes/auth.py` |
| CSRF and origin protection | Mutating requests require valid CSRF and trusted origins | `tests/test_core.py`, `utils/security.py`, `routes/middleware.py` |
| Error shielding | Internal error details stay out of browser responses, request IDs remain visible | `tests/test_core.py`, `utils/errors.py` |
| Chat rooms | Creation, loading, empty-chat cleanup, pinning/order behavior | `tests/test_ui_flows.py`, `routes/api.py`, `services/room_service.py` |
| Chat branching | Parent/child messages, active branch path, pruning future artifacts | `tests/test_core.py`, `tests/test_ui_flows.py`, `services/chat_service.py` |
| Auto titles | Fast title model `llama3.2:1b`, title cleanup, room update | `tests/test_core.py`, `services/ollama_service.py`, `config.py` |
| Artifact history | Save, dedupe, delete, API protection, ZIP/export contracts | `tests/test_core.py`, `tests/test_ui_flows.py`, `services/artifact_service.py` |
| Live preview | iframe sandbox, tabs, reload controls, console/error bridge | `tests/test_core.py`, `static/js/artifacts.js`, `templates/index.html` |
| Rich chat rendering | Mermaid, Chart.js, color tags, rich-library loading | `tests/test_core.py`, `tests/test_ui_flows.py`, `static/js/chat.js` |
| Pyodide | Loader contract, browser Python tab, error handling surface | `tests/test_core.py`, `static/js/artifacts.js` |
| Dashboard | Metrics, token explanation, privacy center, debug center, filters | `tests/test_core.py`, `tests/test_ui_flows.py`, `templates/dashboard.html` |
| Backups | SQLite backup creation, checksum manifest, verification failure detection | `tests/test_core.py`, `services/backup_service.py` |
| Health checks | Database, logs, backups, Ollama warnings | `tests/test_core.py`, `utils/system_health.py` |
| Privacy tools | Local data summary, protected purge flow, backup cleanup | `tests/test_core.py`, `utils/privacy.py` |
| Release documentation | README/security/testing contracts and private-file rules | `tests/test_core.py`, `README.md`, `SECURITY.md`, `.gitignore` |

### 3. Cross-Platform Test Matrix

LEON AI is a Flask + SQLite + Vanilla JS application and is designed to be portable wherever Python and Ollama are available. The macOS start script is optimized for local Mac usage; Windows and Linux can run the app through the same Python backend with platform-specific startup steps.

| Platform | Status | What to verify |
| --- | --- | --- |
| macOS Apple Silicon | Primary release target | `Starten.command`, Ollama detection, Safari/Chrome rendering, local paths, backups, logs |
| macOS Intel | Supported macOS target | Same macOS checklist, with additional dependency install verification |
| Windows laptops/desktops | Supported cross-platform target | Python virtual environment, `pip install -r requirements.txt`, Ollama for Windows, browser rendering, local database paths |
| Linux | Compatible architecture / optional target | Python virtual environment, Ollama service, localhost binding, file permissions, browser rendering |

Recommended Windows/Linux start pattern:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# Windows PowerShell: .\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

### 4. Functional Tests

| Function | Expected behavior | Failure mode checked |
| --- | --- | --- |
| Module initialization | Routes, services, database tables, and templates load correctly | Missing tables or broken imports fail tests |
| Flask backend stability | Local test client handles login, API calls, mutations, and dashboard routes | 403/500 handling stays controlled |
| AI interface handling | Ollama availability, model listing, auto-title payloads, timeout/error paths | Offline Ollama returns safe warnings |
| Artifact system | Generated HTML/CSS/JS/Python snippets are saved, versioned, previewed, and exportable | Duplicate versions are deduped; deleted versions are removed |
| Chat branching | Editing from older messages can create a new path without corrupting existing history | Active branch path is built from selected leaf |
| Backup system | Backups include integrity metadata and can detect modified files | Modified backup verification fails safely |

### 5. UI/UX Tests

| UI area | What is checked |
| --- | --- |
| Login and first setup | CSRF fields, setup screen, profile creation, automatic login after setup |
| Chat shell | Sidebar, chat list, pinned chats, model selector, status controls, input area |
| Rich messages | Mermaid diagrams, Chart.js graphs, colored text markers, code blocks |
| Artifact panel | Preview, Code, Terminal, Error tabs, reload button, fullscreen mode |
| Dashboard | Activity filters, token explanation, privacy tools, debug center, charts |
| Responsive behavior | Laptop displays and external monitors should keep controls readable and panels usable |

Manual responsive checks:

- 13-inch laptop width.
- 15/16-inch laptop width.
- External monitor width.
- Light and dark theme.
- Long chat names.
- Long generated code blocks.
- Artifact panel opened and closed.

### 6. Error Handling Tests

| Scenario | Expected behavior |
| --- | --- |
| Missing or offline Ollama | The app shows a safe warning instead of crashing. |
| Wrong password | Login remains blocked and no sensitive details are shown. |
| Missing `.env` values | Defaults are used where safe; required secrets should be set before release. |
| Invalid CSRF token | Mutating request is rejected with `403`. |
| Cross-origin mutation attempt | Request is blocked by origin checks. |
| Internal backend error | Browser receives a clean message and request ID, not a stack trace. |
| Broken generated preview code | Preview error tab/console captures the issue without breaking the main app. |
| Missing internet/CDN dependency | Rich preview libraries may fail gracefully; core local chat remains available. |
| Wrong external API key | External provider calls should fail with a controlled error, not expose the key. |

### 7. Manual QA Checklist Before A Release

1. Start LEON AI locally.
2. Open `http://127.0.0.1:5001`.
3. Complete first setup on a fresh data directory.
4. Log out and log in again.
5. Create a new chat and send a German message.
6. Confirm the assistant remains in German when the user writes German.
7. Generate a simple HTML page and confirm the preview panel renders visible content.
8. Open the Artifact panel tabs: Preview, Code, Terminal, Errors.
9. Click the preview reload button.
10. Ask for a Mermaid diagram and confirm it renders as a diagram.
11. Ask for a Chart.js bar chart and confirm it renders as a chart.
12. Ask for colored text such as `[rot]Example[/rot]` and confirm the color appears.
13. Edit an older message and confirm a new branch is created.
14. Pin a chat and confirm it stays at the top.
15. Open the dashboard and check metrics, token explanation, charts, privacy tools, and debug center.
16. Run a backup and confirm the health check reports it correctly.
17. Check `data/logs/leon.log` for unexpected `ERROR` lines.
18. Confirm `.env`, `data/`, `backup/`, `venv/`, databases, and logs are not staged.

### 8. Known Expected Test Logs

Some automated tests intentionally trigger failures to prove security and error shielding work. These log lines can appear during testing and are expected if the final unittest result is `OK`.

| Expected test log | Why it appears |
| --- | --- |
| `403` | CSRF and origin-protection tests intentionally send invalid requests. |
| `500` | Hidden-error tests intentionally trigger backend errors. |
| Internal test detail in local log | The local log may contain debug information, but the browser response must not expose it. |

### 9. Release Rule

A release is ready only when:

- Automated tests pass.
- JavaScript syntax checks pass.
- Manual preview checks pass.
- Mermaid, Chart.js, Pyodide, colored text, and artifacts are verified.
- Security notes are current.
- Testing notes are current.
- `.env`, `data/`, `backup/`, `venv/`, databases, logs, and tokens are not staged for Git.

---

## Deutsche Version

### 1. Schnelle Testbefehle

Vollständige automatisierte Test-Suite ausführen:

```bash
./venv/bin/python -m unittest discover -s tests -q
```

Dieselbe Suite mit ausführlicher Ausgabe:

```bash
./venv/bin/python -m unittest discover -s tests -v
```

Frontend-JavaScript auf Syntaxfehler prüfen:

```bash
node --check static/js/api.js
node --check static/js/ui.js
node --check static/js/artifacts.js
node --check static/js/chat.js
```

Patch-/Leerzeichenprobleme vor dem Commit prüfen:

```bash
git diff --check
```

### 2. Aktuelle automatisierte Abdeckung

Die aktuelle automatisierte Suite umfasst **46 Tests** für Backend-Verhalten, Frontend-Verträge, Sicherheitskontrollen, Artifacts, Datenschutz-Werkzeuge, Backups und UI-Flow-Erwartungen.

| Testbereich | Was geprüft wird | Wichtigste Belege |
| --- | --- | --- |
| Datenbank-Migrationen | Parent-IDs, Artifact-Versionstabellen, Schema-Kompatibilität | `tests/test_core.py`, `models/database.py` |
| Authentifizierung | Login, geschützte Seiten, First Setup, Session-Status | `tests/test_core.py`, `tests/test_ui_flows.py`, `routes/auth.py` |
| CSRF- und Origin-Schutz | Schreibende Requests benötigen gültige CSRF-Tokens und vertrauenswürdige Origins | `tests/test_core.py`, `utils/security.py`, `routes/middleware.py` |
| Fehlerabschirmung | Interne Fehlerdetails bleiben aus Browser-Antworten heraus, Request-IDs bleiben sichtbar | `tests/test_core.py`, `utils/errors.py` |
| Chat-Räume | Erstellung, Laden, Aufräumen leerer Chats, angepinnte Reihenfolge | `tests/test_ui_flows.py`, `routes/api.py`, `services/room_service.py` |
| Chat-Branching | Parent-/Child-Nachrichten, aktiver Ast, Entfernen zukünftiger Artifacts | `tests/test_core.py`, `tests/test_ui_flows.py`, `services/chat_service.py` |
| Auto-Titel | Schnelles Titelmodell `llama3.2:1b`, Titelbereinigung, Raum-Update | `tests/test_core.py`, `services/ollama_service.py`, `config.py` |
| Artifact-Verlauf | Speichern, Dedupe, Löschen, API-Schutz, ZIP-/Export-Verträge | `tests/test_core.py`, `tests/test_ui_flows.py`, `services/artifact_service.py` |
| Live-Vorschau | iframe-Sandbox, Tabs, Aktualisieren, Konsolen-/Fehlerbrücke | `tests/test_core.py`, `static/js/artifacts.js`, `templates/index.html` |
| Rich Chat Rendering | Mermaid, Chart.js, Farbtags, Laden der Rich-Libraries | `tests/test_core.py`, `tests/test_ui_flows.py`, `static/js/chat.js` |
| Pyodide | Loader-Vertrag, Browser-Python-Tab, sichtbare Fehlerbehandlung | `tests/test_core.py`, `static/js/artifacts.js` |
| Dashboard | Metriken, Token-Erklärung, Privacy Center, Debug Center, Filter | `tests/test_core.py`, `tests/test_ui_flows.py`, `templates/dashboard.html` |
| Backups | SQLite-Backup, Checksum-Manifest, Erkennung geänderter Backups | `tests/test_core.py`, `services/backup_service.py` |
| Health Checks | Datenbank, Logs, Backups, Ollama-Warnungen | `tests/test_core.py`, `utils/system_health.py` |
| Datenschutz-Werkzeuge | Lokale Datenübersicht, geschütztes Löschen, Backup-Bereinigung | `tests/test_core.py`, `utils/privacy.py` |
| Release-Dokumentation | README-/Security-/Testing-Verträge und Regeln für private Dateien | `tests/test_core.py`, `README.md`, `SECURITY.md`, `.gitignore` |

### 3. Cross-Platform-Testmatrix

LEON AI ist eine Flask-, SQLite- und Vanilla-JS-Anwendung und so aufgebaut, dass sie überall laufen kann, wo Python und Ollama verfügbar sind. Das macOS-Startskript ist für lokale Mac-Nutzung optimiert; Windows und Linux können denselben Python-Backend-Weg mit plattformspezifischem Start nutzen.

| Plattform | Status | Was geprüft werden sollte |
| --- | --- | --- |
| macOS Apple Silicon | Primäres Release-Ziel | `Starten.command`, Ollama-Erkennung, Safari-/Chrome-Rendering, lokale Pfade, Backups, Logs |
| macOS Intel | Unterstütztes macOS-Ziel | Gleiche macOS-Checkliste plus zusätzliche Prüfung der Abhängigkeitsinstallation |
| Windows-Laptops/-Desktops | Unterstütztes Cross-Platform-Ziel | Python-Umgebung, `pip install -r requirements.txt`, Ollama für Windows, Browser-Rendering, lokale Datenbankpfade |
| Linux | Kompatible Architektur / optionales Ziel | Python-Umgebung, Ollama-Service, localhost-Bindung, Dateirechte, Browser-Rendering |

Empfohlenes Startmuster für Windows/Linux:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# Windows PowerShell: .\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

### 4. Funktionale Tests

| Funktion | Erwartetes Verhalten | Geprüfter Fehlerfall |
| --- | --- | --- |
| Modul-Initialisierung | Routen, Services, Datenbanktabellen und Templates laden korrekt | Fehlende Tabellen oder defekte Imports lassen Tests fehlschlagen |
| Flask-Backend-Stabilität | Lokaler Test-Client verarbeitet Login, API-Aufrufe, Mutationen und Dashboard-Routen | 403-/500-Behandlung bleibt kontrolliert |
| KI-Schnittstellen | Ollama-Erreichbarkeit, Modellliste, Auto-Titel-Payloads, Timeout-/Fehlerpfade | Offline-Ollama gibt sichere Warnungen zurück |
| Artifact-System | Generierte HTML-/CSS-/JS-/Python-Snippets werden gespeichert, versioniert, angezeigt und exportiert | Doppelte Versionen werden dedupliziert; gelöschte Versionen verschwinden |
| Chat-Branching | Bearbeiten älterer Nachrichten erzeugt neue Pfade, ohne bestehenden Verlauf zu beschädigen | Aktiver Ast wird aus ausgewähltem Leaf aufgebaut |
| Backup-System | Backups enthalten Integritätsmetadaten und erkennen geänderte Dateien | Geänderte Backup-Prüfung schlägt kontrolliert fehl |

### 5. UI-/UX-Tests

| UI-Bereich | Was geprüft wird |
| --- | --- |
| Login und First Setup | CSRF-Felder, Setup-Screen, Profilerstellung, automatischer Login nach Setup |
| Chat-Oberfläche | Sidebar, Chatliste, angepinnte Chats, Modellwahl, Status-Steuerung, Eingabebereich |
| Rich Messages | Mermaid-Diagramme, Chart.js-Grafiken, farbige Textmarker, Code-Blöcke |
| Artifact-Panel | Vorschau, Code, Terminal, Fehler-Tabs, Aktualisieren-Button, Vollbildmodus |
| Dashboard | Aktivitätsfilter, Token-Erklärung, Privacy Tools, Debug Center, Diagramme |
| Responsives Verhalten | Laptop-Displays und externe Monitore sollen Bedienelemente lesbar und Panels nutzbar halten |

Manuelle Responsive-Prüfungen:

- 13-Zoll-Laptopbreite.
- 15-/16-Zoll-Laptopbreite.
- Externer Monitor.
- Helles und dunkles Theme.
- Lange Chatnamen.
- Lange generierte Code-Blöcke.
- Artifact-Panel geöffnet und geschlossen.

### 6. Fehlerbehandlung

| Szenario | Erwartetes Verhalten |
| --- | --- |
| Fehlendes oder offline Ollama | Die App zeigt eine sichere Warnung statt abzustürzen. |
| Falsches Passwort | Login bleibt blockiert und zeigt keine sensiblen Details. |
| Fehlende `.env`-Werte | Sichere Defaults werden genutzt, wo möglich; wichtige Secrets sollten vor Releases gesetzt sein. |
| Ungültiger CSRF-Token | Schreibender Request wird mit `403` abgelehnt. |
| Cross-Origin-Schreibversuch | Request wird durch Origin-Checks blockiert. |
| Interner Backend-Fehler | Browser erhält saubere Meldung mit Request-ID statt Stacktrace. |
| Fehlerhafter generierter Vorschau-Code | Fehler-Tab/Konsole erfasst das Problem, ohne die Haupt-App zu beschädigen. |
| Fehlende Internetverbindung/CDN-Abhängigkeit | Rich-Preview-Bibliotheken können kontrolliert ausfallen; der lokale Chat-Kern bleibt verfügbar. |
| Falscher externer API-Key | Externe Anbieteraufrufe sollen kontrolliert fehlschlagen, ohne den Schlüssel offenzulegen. |

### 7. Manuelle QA-Checkliste vor einem Release

1. LEON AI lokal starten.
2. `http://127.0.0.1:5001` öffnen.
3. First Setup mit frischem Datenordner abschließen.
4. Ausloggen und erneut einloggen.
5. Neuen Chat erstellen und deutsche Nachricht senden.
6. Prüfen, dass der Assistent bei deutscher Nutzereingabe auf Deutsch bleibt.
7. Einfache HTML-Seite erzeugen und sichtbare Vorschau bestätigen.
8. Artifact-Panel-Tabs öffnen: Vorschau, Code, Terminal, Fehler.
9. Aktualisieren-Button der Vorschau klicken.
10. Mermaid-Diagramm anfordern und gerenderte Diagrammansicht prüfen.
11. Chart.js-Balkendiagramm anfordern und gerenderten Chart prüfen.
12. Farbigen Text wie `[rot]Beispiel[/rot]` anfordern und sichtbare Farbe prüfen.
13. Ältere Nachricht bearbeiten und neuen Ast bestätigen.
14. Chat anpinnen und Reihenfolge prüfen.
15. Dashboard öffnen und Metriken, Token-Erklärung, Diagramme, Privacy Tools und Debug Center prüfen.
16. Backup ausführen und korrekten Health-Check prüfen.
17. `data/logs/leon.log` auf unerwartete `ERROR`-Zeilen prüfen.
18. Prüfen, dass `.env`, `data/`, `backup/`, `venv/`, Datenbanken und Logs nicht für Git vorgemerkt sind.

### 8. Erwartete Test-Logs

Einige automatisierte Tests lösen absichtlich Fehler aus, um Sicherheit und Fehlerabschirmung zu prüfen. Diese Log-Zeilen können während der Tests erscheinen und sind erwartbar, wenn das endgültige unittest-Ergebnis `OK` ist.

| Erwarteter Test-Log | Warum er erscheint |
| --- | --- |
| `403` | CSRF- und Origin-Schutztests senden absichtlich ungültige Requests. |
| `500` | Hidden-Error-Tests lösen absichtlich Backend-Fehler aus. |
| Interne Testdetails im lokalen Log | Das lokale Log darf Debug-Informationen enthalten; die Browser-Antwort darf sie nicht zeigen. |

### 9. Release-Regel

Ein Release gilt erst als bereit, wenn:

- automatisierte Tests erfolgreich sind,
- JavaScript-Syntaxprüfungen erfolgreich sind,
- manuelle Vorschau-Checks erfolgreich sind,
- Mermaid, Chart.js, Pyodide, Farbtags und Artifacts geprüft wurden,
- Sicherheitshinweise aktuell sind,
- Testing-Hinweise aktuell sind,
- `.env`, `data/`, `backup/`, `venv/`, Datenbanken, Logs und Tokens nicht für Git vorgemerkt sind.
