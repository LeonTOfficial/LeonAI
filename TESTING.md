# LEON AI Testing

![Tests](https://img.shields.io/badge/tests-46%20automated-17a673?style=for-the-badge)
![Backend](https://img.shields.io/badge/backend-Flask-111827?style=for-the-badge)
![Frontend](https://img.shields.io/badge/frontend-vanilla%20JS-5357ff?style=for-the-badge)
![QA](https://img.shields.io/badge/QA-release%20checklist-d99b18?style=for-the-badge)

> 🇩🇪 **German version available:** [Click here for the German description](#german-version)

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

### 2. GitHub Actions / CI

LEON AI uses a small ready-made GitHub Actions workflow instead of a custom runner. The workflow lives in [`.github/workflows/test.yml`](.github/workflows/test.yml) and runs on every push or pull request to `main`.

| Check | Tool | Why it exists |
| --- | --- | --- |
| Repository checkout | `actions/checkout@v4` | Uses the official GitHub checkout action. |
| Python setup | `actions/setup-python@v5` | Installs the supported Python versions consistently. |
| Node setup | `actions/setup-node@v4` | Provides Node.js for frontend syntax checks. |
| Backend tests | `python -m unittest discover -s tests -q` | Verifies Flask routes, services, security, database, artifacts, and UI contracts. |
| Frontend syntax | `node --check static/js/*.js` | Catches JavaScript syntax breakage before release. |

The CI matrix intentionally uses **Python 3.11 and 3.12**. Python 3.9 is not included because the project uses modern Python syntax such as `str | None`, which requires Python 3.10 or newer.

### 3. Current Automated Coverage

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

### 4. Cross-Platform Test Matrix

LEON AI is a Flask + SQLite + Vanilla JS application and is designed to be portable wherever Python and Ollama are available. macOS includes a convenience launcher, while Windows and Linux run the same Python backend through their normal terminal workflow.

| Platform | Status | What to verify |
| --- | --- | --- |
| macOS Apple Silicon | Supported local target | `Starten.command`, Ollama detection, Safari/Chrome rendering, local paths, backups, logs |
| macOS Intel | Supported local target | Same macOS behavior, with additional dependency install verification |
| Windows laptops/desktops | Supported local target | Python virtual environment, `pip install -r requirements.txt`, Ollama for Windows, browser rendering, local database paths |
| Linux | Compatible local target | Python virtual environment, Ollama service, localhost binding, file permissions, browser rendering |

Recommended Windows/Linux start pattern:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# Windows PowerShell: .\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

### 5. Functional Tests

| Function | Expected behavior | Failure mode checked |
| --- | --- | --- |
| Module initialization | Routes, services, database tables, and templates load correctly | Missing tables or broken imports fail tests |
| Flask backend stability | Local test client handles login, API calls, mutations, and dashboard routes | 403/500 handling stays controlled |
| AI interface handling | Ollama availability, model listing, auto-title payloads, timeout/error paths | Offline Ollama returns safe warnings |
| Artifact system | Generated HTML/CSS/JS/Python snippets are saved, versioned, previewed, and exportable | Duplicate versions are deduped; deleted versions are removed |
| Chat branching | Editing from older messages can create a new path without corrupting existing history | Active branch path is built from selected leaf |
| Backup system | Backups include integrity metadata and can detect modified files | Modified backup verification fails safely |

### 6. UI/UX Tests

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

### 7. Error Handling Tests

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

### 8. Manual QA Story

Manual QA describes the real user journey that the automated tests cannot fully see. It is less about clicking through a rigid list and more about proving that LEON AI feels complete as a local AI workspace.

| User journey | What this proves |
| --- | --- |
| First launch and first setup | A new user can create a profile, set a password, and enter the workspace without touching code. |
| Login and new chat | The protected app shell, room list, model selector, and empty-chat behavior work together. |
| German conversation | The assistant respects German input and keeps the language consistent. |
| HTML/CSS/JS generation | The chat and artifact panel cooperate so generated code becomes a visible preview, not just text. |
| Mermaid and Chart.js output | Native diagrams and charts render directly in the conversation. |
| Colored text markers | The chat renderer can display structured color annotations such as nouns, verbs, or key ideas. |
| Branching and pinned chats | Longer conversations can be reorganized without losing the original path. |
| Dashboard and privacy center | Activity, tokens, logs, health, backups, and privacy tools are visible in one place. |
| Logs and request IDs | When something fails, the browser message and `data/logs/leon.log` can be connected through clear diagnostic information. |

### 9. Known Expected Test Logs

Some automated tests intentionally trigger failures to prove security and error shielding work. These log lines can appear during testing and are expected if the final unittest result is `OK`.

| Expected test log | Why it appears |
| --- | --- |
| `403` | CSRF and origin-protection tests intentionally send invalid requests. |
| `500` | Hidden-error tests intentionally trigger backend errors. |
| Internal test detail in local log | The local log may contain debug information, but the browser response must not expose it. |

### 10. Release Readiness

LEON AI is considered release-ready when the technical tests and the product story agree with each other: the automated suite passes, the JavaScript files parse correctly, the preview panel works in a browser, and the documentation describes the current behavior honestly.

| Release signal | Meaning |
| --- | --- |
| Unit tests pass | Backend behavior, security contracts, artifacts, privacy tools, backups, and UI contracts match the expected model. |
| JavaScript checks pass | The frontend modules can load without syntax-level breakage. |
| Manual preview works | Generated HTML/CSS/JS, Mermaid, Chart.js, Pyodide, and color tags are usable in the real interface. |
| Documentation is current | README, architecture, security, and testing files explain the same product that users actually download. |
| Private files stay local | `.env`, `data/`, `backup/`, `venv/`, databases, logs, and tokens stay out of the public repository. |

---

<a id="german-version"></a>

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

### 2. GitHub Actions / CI

LEON AI nutzt einen kleinen fertigen GitHub-Actions-Workflow statt eines selbstgebauten CI-Runners. Der Workflow liegt in [`.github/workflows/test.yml`](.github/workflows/test.yml) und läuft bei jedem Push oder Pull Request auf `main`.

| Prüfung | Werkzeug | Warum es das gibt |
| --- | --- | --- |
| Repository auschecken | `actions/checkout@v4` | Nutzt die offizielle Checkout-Action von GitHub. |
| Python einrichten | `actions/setup-python@v5` | Installiert die unterstützten Python-Versionen einheitlich. |
| Node einrichten | `actions/setup-node@v4` | Stellt Node.js für Frontend-Syntaxprüfungen bereit. |
| Backend-Tests | `python -m unittest discover -s tests -q` | Prüft Flask-Routen, Services, Sicherheit, Datenbank, Artifacts und UI-Verträge. |
| Frontend-Syntax | `node --check static/js/*.js` | Findet JavaScript-Syntaxfehler vor dem Release. |

Die CI-Matrix nutzt bewusst **Python 3.11 und 3.12**. Python 3.9 ist nicht enthalten, weil das Projekt moderne Python-Syntax wie `str | None` verwendet. Diese Schreibweise braucht Python 3.10 oder neuer.

### 3. Aktuelle automatisierte Abdeckung

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

### 4. Cross-Platform-Testmatrix

LEON AI ist eine Flask-, SQLite- und Vanilla-JS-Anwendung und so aufgebaut, dass sie überall laufen kann, wo Python und Ollama verfügbar sind. macOS bringt einen Komfort-Starter mit, während Windows und Linux dasselbe Python-Backend über ihren normalen Terminal-Weg starten.

| Plattform | Status | Was geprüft werden sollte |
| --- | --- | --- |
| macOS Apple Silicon | Unterstütztes lokales Ziel | `Starten.command`, Ollama-Erkennung, Safari-/Chrome-Rendering, lokale Pfade, Backups, Logs |
| macOS Intel | Unterstütztes lokales Ziel | Gleiches macOS-Verhalten plus zusätzliche Prüfung der Abhängigkeitsinstallation |
| Windows-Laptops/-Desktops | Unterstütztes lokales Ziel | Python-Umgebung, `pip install -r requirements.txt`, Ollama für Windows, Browser-Rendering, lokale Datenbankpfade |
| Linux | Kompatibles lokales Ziel | Python-Umgebung, Ollama-Service, localhost-Bindung, Dateirechte, Browser-Rendering |

Empfohlenes Startmuster für Windows/Linux:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# Windows PowerShell: .\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

### 5. Funktionale Tests

| Funktion | Erwartetes Verhalten | Geprüfter Fehlerfall |
| --- | --- | --- |
| Modul-Initialisierung | Routen, Services, Datenbanktabellen und Templates laden korrekt | Fehlende Tabellen oder defekte Imports lassen Tests fehlschlagen |
| Flask-Backend-Stabilität | Lokaler Test-Client verarbeitet Login, API-Aufrufe, Mutationen und Dashboard-Routen | 403-/500-Behandlung bleibt kontrolliert |
| KI-Schnittstellen | Ollama-Erreichbarkeit, Modellliste, Auto-Titel-Payloads, Timeout-/Fehlerpfade | Offline-Ollama gibt sichere Warnungen zurück |
| Artifact-System | Generierte HTML-/CSS-/JS-/Python-Snippets werden gespeichert, versioniert, angezeigt und exportiert | Doppelte Versionen werden dedupliziert; gelöschte Versionen verschwinden |
| Chat-Branching | Bearbeiten älterer Nachrichten erzeugt neue Pfade, ohne bestehenden Verlauf zu beschädigen | Aktiver Ast wird aus ausgewähltem Leaf aufgebaut |
| Backup-System | Backups enthalten Integritätsmetadaten und erkennen geänderte Dateien | Geänderte Backup-Prüfung schlägt kontrolliert fehl |

### 6. UI-/UX-Tests

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

### 7. Fehlerbehandlung

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

### 8. Manuelle QA-Geschichte

Manuelle QA beschreibt den echten Nutzerweg, den automatisierte Tests nicht vollständig sehen können. Es geht weniger um eine starre Klickliste und mehr darum, zu beweisen, dass LEON AI sich als lokaler KI-Arbeitsbereich vollständig anfühlt.

| Nutzerweg | Was dadurch sichtbar wird |
| --- | --- |
| Erster Start und First Setup | Ein neuer Nutzer kann Profil und Passwort einrichten und ohne Code-Berührung in den Arbeitsbereich starten. |
| Login und neuer Chat | Geschützte App-Oberfläche, Raumliste, Modellwahl und Verhalten leerer Chats greifen ineinander. |
| Deutsche Unterhaltung | Der Assistent respektiert deutsche Eingaben und hält die Sprache konsistent. |
| HTML/CSS/JS-Erzeugung | Chat und Artifact-Panel arbeiten zusammen, sodass generierter Code als sichtbare Vorschau erscheint. |
| Mermaid- und Chart.js-Ausgabe | Native Diagramme und Charts werden direkt in der Unterhaltung gerendert. |
| Farbige Textmarker | Der Chat-Renderer kann strukturierte Farbmarkierungen wie Nomen, Verben oder Schlüsselideen anzeigen. |
| Branching und angepinnte Chats | Längere Gespräche können neu organisiert werden, ohne den ursprünglichen Pfad zu verlieren. |
| Dashboard und Privacy Center | Aktivität, Tokens, Logs, Health, Backups und Datenschutz-Werkzeuge sind an einem Ort sichtbar. |
| Logs und Request-IDs | Wenn etwas fehlschlägt, lassen sich Browser-Meldung und `data/logs/leon.log` über Diagnoseinformationen verbinden. |

### 9. Erwartete Test-Logs

Einige automatisierte Tests lösen absichtlich Fehler aus, um Sicherheit und Fehlerabschirmung zu prüfen. Diese Log-Zeilen können während der Tests erscheinen und sind erwartbar, wenn das endgültige unittest-Ergebnis `OK` ist.

| Erwarteter Test-Log | Warum er erscheint |
| --- | --- |
| `403` | CSRF- und Origin-Schutztests senden absichtlich ungültige Requests. |
| `500` | Hidden-Error-Tests lösen absichtlich Backend-Fehler aus. |
| Interne Testdetails im lokalen Log | Das lokale Log darf Debug-Informationen enthalten; die Browser-Antwort darf sie nicht zeigen. |

### 10. Release-Reife

LEON AI gilt als releasefähig, wenn technische Tests und Produktgeschichte zusammenpassen: Die automatisierte Suite läuft durch, die JavaScript-Dateien sind syntaktisch sauber, das Vorschau-Panel funktioniert im Browser und die Dokumentation beschreibt ehrlich den aktuellen Stand.

| Release-Signal | Bedeutung |
| --- | --- |
| Unit Tests laufen durch | Backend-Verhalten, Sicherheitsverträge, Artifacts, Datenschutz-Werkzeuge, Backups und UI-Verträge passen zum erwarteten Modell. |
| JavaScript-Prüfungen laufen durch | Die Frontend-Module können ohne Syntaxbruch geladen werden. |
| Manuelle Vorschau funktioniert | Generiertes HTML/CSS/JS, Mermaid, Chart.js, Pyodide und Farbtags sind in der echten Oberfläche nutzbar. |
| Dokumentation ist aktuell | README, Architektur, Sicherheit und Testing erklären dasselbe Produkt, das Nutzer herunterladen. |
| Private Dateien bleiben lokal | `.env`, `data/`, `backup/`, `venv/`, Datenbanken, Logs und Tokens bleiben außerhalb des öffentlichen Repositorys. |
