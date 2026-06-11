# LEON AI Updates

![Changelog](https://img.shields.io/badge/changelog-active-5357ff?style=for-the-badge)
![Logs](https://img.shields.io/badge/logs-structured-111827?style=for-the-badge)
![CI](https://img.shields.io/badge/GitHub%20Actions-ready-17a673?style=for-the-badge)

> 🇩🇪 **German version available:** [Click here for the German description](#german-version)

## English Version

### What This File Is For

`UPDATES.md` is the release memory of LEON AI. It explains what changed, why it changed, where important behavior lives, and how problems can be traced through logs and tests.

It is not only a checklist. It should help a new developer understand the project history and the thinking behind major updates.

Related documents:

| Document | Purpose |
| --- | --- |
| [`README.md`](README.md) | Public project overview and installation. |
| [`STRUKTUR.md`](STRUKTUR.md) | Architecture, folders, data flow, and module ownership. |
| [`SECURITY.md`](SECURITY.md) | Security model, local data, secrets, and responsible disclosure. |
| [`TESTING.md`](TESTING.md) | Automated tests, manual QA, and release readiness. |

### How A Log Entry Is Built

LEON AI writes structured runtime logs to `data/logs/leon.log`. The log format is defined in [`utils/logging.py`](utils/logging.py) and enriched by request IDs from [`routes/middleware.py`](routes/middleware.py).

```text
2026-06-11 15:42:10 | INFO     | a1b2c3d4e5f6 | leon.activity | log_activity:82 | Chat geöffnet
```

| Part | Meaning | Why it matters |
| --- | --- | --- |
| `2026-06-11 15:42:10` | Timestamp | Shows when the event happened. |
| `INFO` | Log level | Shows whether the event is normal, suspicious, or broken. |
| `a1b2c3d4e5f6` | Request ID | Connects a browser error with the matching backend log line. |
| `leon.activity` | Logger/module | Shows which part of LEON AI wrote the log. |
| `log_activity:82` | Function and line | Points to the code location that produced the entry. |
| `Chat geöffnet` | Message | Human-readable explanation of the event. |

### Log Levels

| Level | Meaning | Typical example |
| --- | --- | --- |
| `INFO` | Normal app activity | Chat opened, login successful, dashboard opened. |
| `WARNING` | Something needs attention, but the app can continue | Offline model, blocked request, missing optional asset. |
| `ERROR` | A feature failed and should be investigated | Database write failed, unexpected backend exception. |
| `CRITICAL` | Severe failure that can stop the app | Startup failure, unrecoverable configuration problem. |

### How Terminal Activity Works

The nice terminal activity lines are created by `log_activity()` in [`utils/logging.py`](utils/logging.py). They are separate from the detailed file log:

```text
🌐  15:42:10  Chat geöffnet
➕  15:42:14  Neuer Chat erstellt
📂  15:42:15  Chat lädt
💬  15:42:30  Nachricht "Erstelle eine HTML-Seite"
```

| Setting | Behavior |
| --- | --- |
| `LEON_TERMINAL_ACTIVITY=1` | Shows friendly live activity in the terminal. |
| `LEON_TERMINAL_LOG_LEVEL=CRITICAL` | Keeps technical logs quiet unless something severe happens. |
| `data/logs/leon.log` | Always keeps the structured developer log locally. |

This gives two views of the same system: a clean user-friendly terminal and a detailed local debug log.

### How To Use Logs When Something Breaks

Use the log file to move from “something is broken” to “this exact function failed”.

```bash
tail -n 80 data/logs/leon.log
grep -E "ERROR|WARNING|CRITICAL" data/logs/leon.log
grep "a1b2c3d4e5f6" data/logs/leon.log
```

| Situation | What to look for |
| --- | --- |
| Browser shows a request ID | Search that ID in `data/logs/leon.log`. |
| Preview stays empty | Search for `Artifact`, `iframe`, `preview`, `ERROR`, or browser console output in the panel. |
| Login fails | Check for `auth`, `403`, and CSRF/origin messages. |
| Ollama does not answer | Check health warnings and whether Ollama is reachable at `localhost:11434`. |

Do not publish full logs publicly if they contain personal prompts, local paths, or project details.

### GitHub Actions: Use A Ready Standard Workflow

For this project, the cleanest option is to use official ready-made GitHub Actions instead of building a custom CI runner from scratch.

| Decision | Choice |
| --- | --- |
| Checkout | `actions/checkout@v4` |
| Python setup | `actions/setup-python@v5` |
| Node setup | `actions/setup-node@v4` |
| Test command | `python -m unittest discover -s tests -q` |
| JS syntax check | `node --check static/js/*.js` |
| Workflow file | [`.github/workflows/test.yml`](.github/workflows/test.yml) |

The workflow intentionally uses **Python 3.11 and 3.12**. Python 3.9 is not used because LEON AI uses modern Python syntax such as `str | None`, which is supported from Python 3.10 onward.

### Older Python Versions

If LEON AI is started with an old Python version, errors can appear before the app even reaches the browser.

| Problem | Why it happens | Fix |
| --- | --- | --- |
| `SyntaxError` near `str \| None` | Python 3.9 does not understand modern union type hints. | Use Python 3.11 or newer. |
| Dependency install fails | Newer Flask/dependency versions may require newer Python. | Upgrade Python and recreate the virtual environment. |
| Tests behave differently | Older runtimes can differ in typing, imports, and SSL behavior. | Run the same version as CI. |

Recommended local check:

```bash
python --version
python -m unittest discover -s tests -q
```

### Update Entry Template

New entries should be added at the top of the changelog section.

```markdown
## [YYYY-MM-DD] Short Title

**Type:** Added | Changed | Fixed | Security | Documentation | Refactoring

### What Changed
- ...

### Why It Matters
- ...

### Files Touched
- `path/to/file.py`

### Verification
- `python -m unittest discover -s tests -q`
```

### Changelog

## [2026-06-11] Documentation Polish And CI Workflow

**Type:** Documentation / CI

### What Changed
- Reworked public documentation into clearer bilingual project information.
- Added a GitHub Actions workflow for Python and JavaScript checks.
- Documented log anatomy, terminal activity, request IDs, and Python version expectations.

### Why It Matters
- New users can understand what LEON AI does without reading the code first.
- Contributors can see which Python versions are supported.
- Bugs can be traced from browser request IDs to local log entries.

### Files Touched
- `README.md`
- `STRUKTUR.md`
- `SECURITY.md`
- `TESTING.md`
- `UPDATES.md`
- `.github/workflows/test.yml`

### Verification
- `python -m unittest discover -s tests -q`
- `node --check static/js/api.js`
- `node --check static/js/ui.js`
- `node --check static/js/artifacts.js`
- `node --check static/js/chat.js`

## [2026-06-04] Log Review And 404 Fixes

**Type:** Fixed / Documentation

### What Changed
- Documented how to inspect `data/logs/leon.log`.
- Added harmless asset handling for browser-requested files such as favicon and Apple touch icons.
- Blocked unsafe relative image paths from AI-generated content.

### Why It Matters
- Browser auto-requests no longer make the log look more broken than the app really is.
- Generated HTML cannot silently reference missing local images in the chat UI.

### Files Touched
- `routes/pages.py`
- `routes/middleware.py`
- `utils/errors.py`
- `static/js/chat.js`
- `STRUKTUR.md`
- `UPDATES.md`

## [2026-06-04] Modular Architecture v4

**Type:** Refactoring

### What Changed
- Split the old monolithic backend into routes, services, models, and utilities.
- Split frontend JavaScript into `api.js`, `ui.js`, `artifacts.js`, and `chat.js`.
- Added structured logging through `utils/logging.py`.

### Why It Matters
- New features can be added without turning `app.py` into a giant file again.
- Bugs are easier to locate because each module owns a clear responsibility.
- Logs now persist locally instead of disappearing in the terminal output.

## [2026-05-31] LEON AI v4 Before Refactoring

**Type:** Added / Changed

### What Changed
- Added password authentication, rate limiting, vision routes, PWA support, token budgeting, and the first live preview panel.
- Improved production defaults and removed aggressive service-worker caching.

### Why It Matters
- This version introduced the first full local AI workspace experience before the modular architecture was created.

---

<a id="german-version"></a>

## Deutsche Version

### Wofür diese Datei da ist

`UPDATES.md` ist das Release-Gedächtnis von LEON AI. Die Datei erklärt, was geändert wurde, warum es geändert wurde, wo wichtiges Verhalten liegt und wie Probleme über Logs und Tests nachvollzogen werden können.

Sie ist nicht nur eine Liste zum Abhaken. Sie soll neuen Entwicklern helfen, die Projektgeschichte und die Entscheidungen hinter größeren Updates zu verstehen.

Verwandte Dokumente:

| Dokument | Zweck |
| --- | --- |
| [`README.md`](README.md) | Öffentliche Projektübersicht und Installation. |
| [`STRUKTUR.md`](STRUKTUR.md) | Architektur, Ordner, Datenfluss und Modulverantwortung. |
| [`SECURITY.md`](SECURITY.md) | Sicherheitsmodell, lokale Daten, Secrets und verantwortliches Melden von Sicherheitslücken. |
| [`TESTING.md`](TESTING.md) | Automatisierte Tests, manuelle QA und Release-Reife. |

### Wie ein Log-Eintrag aufgebaut ist

LEON AI schreibt strukturierte Laufzeit-Logs nach `data/logs/leon.log`. Das Format ist in [`utils/logging.py`](utils/logging.py) definiert und wird durch Request-IDs aus [`routes/middleware.py`](routes/middleware.py) ergänzt.

```text
2026-06-11 15:42:10 | INFO     | a1b2c3d4e5f6 | leon.activity | log_activity:82 | Chat geöffnet
```

| Teil | Bedeutung | Warum das wichtig ist |
| --- | --- | --- |
| `2026-06-11 15:42:10` | Zeitstempel | Zeigt, wann das Ereignis passiert ist. |
| `INFO` | Log-Level | Zeigt, ob das Ereignis normal, auffällig oder kaputt ist. |
| `a1b2c3d4e5f6` | Request-ID | Verbindet einen Browser-Fehler mit der passenden Backend-Logzeile. |
| `leon.activity` | Logger/Modul | Zeigt, welcher Teil von LEON AI den Eintrag geschrieben hat. |
| `log_activity:82` | Funktion und Zeile | Zeigt die Code-Stelle, die den Eintrag erzeugt hat. |
| `Chat geöffnet` | Nachricht | Verständliche Erklärung des Ereignisses. |

### Log-Level

| Level | Bedeutung | Typisches Beispiel |
| --- | --- | --- |
| `INFO` | Normale App-Aktivität | Chat geöffnet, Login erfolgreich, Dashboard geöffnet. |
| `WARNING` | Etwas braucht Aufmerksamkeit, aber die App läuft weiter | Offline-Modell, blockierter Request, fehlendes optionales Asset. |
| `ERROR` | Eine Funktion ist fehlgeschlagen und sollte geprüft werden | Datenbank-Schreibfehler, unerwartete Backend-Exception. |
| `CRITICAL` | Schwerer Fehler, der die App stoppen kann | Startfehler, nicht wiederherstellbares Konfigurationsproblem. |

### Wie die Terminal-Aktivität funktioniert

Die schönen Aktivitätszeilen im Start-Terminal werden über `log_activity()` in [`utils/logging.py`](utils/logging.py) erzeugt. Sie sind getrennt vom detaillierten Datei-Log:

```text
🌐  15:42:10  Chat geöffnet
➕  15:42:14  Neuer Chat erstellt
📂  15:42:15  Chat lädt
💬  15:42:30  Nachricht "Erstelle eine HTML-Seite"
```

| Einstellung | Verhalten |
| --- | --- |
| `LEON_TERMINAL_ACTIVITY=1` | Zeigt freundliche Live-Aktivität im Terminal. |
| `LEON_TERMINAL_LOG_LEVEL=CRITICAL` | Hält technische Logs ruhig, außer etwas Schweres passiert. |
| `data/logs/leon.log` | Speichert immer das strukturierte Entwickler-Log lokal. |

So gibt es zwei Sichten auf dasselbe System: ein ruhiges, nutzerfreundliches Terminal und ein detailliertes lokales Debug-Log.

### Wie man Logs nutzt, wenn etwas kaputtgeht

Mit der Log-Datei kommt man von „irgendetwas ist kaputt“ zu „genau diese Funktion ist fehlgeschlagen“.

```bash
tail -n 80 data/logs/leon.log
grep -E "ERROR|WARNING|CRITICAL" data/logs/leon.log
grep "a1b2c3d4e5f6" data/logs/leon.log
```

| Situation | Wonach du schauen solltest |
| --- | --- |
| Der Browser zeigt eine Request-ID | Suche diese ID in `data/logs/leon.log`. |
| Die Vorschau bleibt leer | Suche nach `Artifact`, `iframe`, `preview`, `ERROR` oder nach Ausgaben im Fehler-Tab des Panels. |
| Login schlägt fehl | Prüfe `auth`, `403` und CSRF-/Origin-Meldungen. |
| Ollama antwortet nicht | Prüfe Health-Warnungen und ob Ollama unter `localhost:11434` erreichbar ist. |

Veröffentliche keine vollständigen Logs, wenn sie persönliche Prompts, lokale Pfade oder Projektdetails enthalten.

### GitHub Actions: fertigen Standard-Workflow nutzen

Für dieses Projekt ist die sauberste Lösung, offizielle fertige GitHub Actions zu verwenden, statt einen eigenen CI-Runner von null selbst zu bauen.

| Entscheidung | Auswahl |
| --- | --- |
| Repository auschecken | `actions/checkout@v4` |
| Python einrichten | `actions/setup-python@v5` |
| Node einrichten | `actions/setup-node@v4` |
| Testbefehl | `python -m unittest discover -s tests -q` |
| JS-Syntaxprüfung | `node --check static/js/*.js` |
| Workflow-Datei | [`.github/workflows/test.yml`](.github/workflows/test.yml) |

Der Workflow nutzt bewusst **Python 3.11 und 3.12**. Python 3.9 wird nicht verwendet, weil LEON AI moderne Python-Syntax wie `str | None` nutzt. Diese Schreibweise funktioniert erst ab Python 3.10.

### Ältere Python-Versionen

Wenn LEON AI mit einer alten Python-Version gestartet wird, können Fehler erscheinen, bevor die App überhaupt im Browser ankommt.

| Problem | Warum es passiert | Lösung |
| --- | --- | --- |
| `SyntaxError` bei `str \| None` | Python 3.9 versteht moderne Union-Type-Hints nicht. | Python 3.11 oder neuer verwenden. |
| Installation von Abhängigkeiten schlägt fehl | Neuere Flask-/Dependency-Versionen können neueres Python verlangen. | Python aktualisieren und die virtuelle Umgebung neu erstellen. |
| Tests verhalten sich anders | Ältere Laufzeiten unterscheiden sich bei Typing, Imports und SSL-Verhalten. | Dieselbe Version wie in CI verwenden. |

Empfohlener lokaler Check:

```bash
python --version
python -m unittest discover -s tests -q
```

### Vorlage für neue Update-Einträge

Neue Einträge gehören oben in den Changelog-Bereich.

```markdown
## [JJJJ-MM-TT] Kurztitel

**Typ:** Hinzugefügt | Geändert | Behoben | Sicherheit | Dokumentation | Refactoring

### Was geändert wurde
- ...

### Warum es wichtig ist
- ...

### Geänderte Dateien
- `pfad/zur/datei.py`

### Prüfung
- `python -m unittest discover -s tests -q`
```

### Changelog

## [2026-06-11] Dokumentations-Feinschliff und CI-Workflow

**Typ:** Dokumentation / CI

### Was geändert wurde
- Öffentliche Dokumentation klarer und zweisprachig aufbereitet.
- GitHub-Actions-Workflow für Python- und JavaScript-Prüfungen ergänzt.
- Log-Aufbau, Terminal-Aktivität, Request-IDs und Python-Versionen dokumentiert.

### Warum es wichtig ist
- Neue Nutzer verstehen LEON AI, ohne zuerst den Code lesen zu müssen.
- Mitwirkende sehen direkt, welche Python-Versionen unterstützt werden.
- Fehler lassen sich von Browser-Request-IDs bis zu lokalen Log-Einträgen zurückverfolgen.

### Geänderte Dateien
- `README.md`
- `STRUKTUR.md`
- `SECURITY.md`
- `TESTING.md`
- `UPDATES.md`
- `.github/workflows/test.yml`

### Prüfung
- `python -m unittest discover -s tests -q`
- `node --check static/js/api.js`
- `node --check static/js/ui.js`
- `node --check static/js/artifacts.js`
- `node --check static/js/chat.js`

## [2026-06-04] Log-Auswertung und 404-Fixes

**Typ:** Behoben / Dokumentation

### Was geändert wurde
- Dokumentiert, wie `data/logs/leon.log` geprüft wird.
- Harmlose Asset-Anfragen des Browsers wie Favicon und Apple-Touch-Icons abgefangen.
- Unsichere relative Bildpfade aus KI-generierten Inhalten blockiert.

### Warum es wichtig ist
- Automatische Browser-Anfragen lassen das Log nicht mehr kaputter aussehen, als die App wirklich ist.
- Generiertes HTML kann in der Chat-Oberfläche nicht still auf fehlende lokale Bilder zeigen.

### Geänderte Dateien
- `routes/pages.py`
- `routes/middleware.py`
- `utils/errors.py`
- `static/js/chat.js`
- `STRUKTUR.md`
- `UPDATES.md`

## [2026-06-04] Modulare Architektur v4

**Typ:** Refactoring

### Was geändert wurde
- Das alte monolithische Backend wurde in Routen, Services, Models und Utilities aufgeteilt.
- Das Frontend-JavaScript wurde in `api.js`, `ui.js`, `artifacts.js` und `chat.js` getrennt.
- Strukturiertes Logging über `utils/logging.py` eingeführt.

### Warum es wichtig ist
- Neue Features können ergänzt werden, ohne `app.py` wieder zu einer riesigen Datei zu machen.
- Fehler sind leichter zu finden, weil jedes Modul eine klare Verantwortung hat.
- Logs bleiben lokal erhalten, statt nur kurz im Terminal sichtbar zu sein.

## [2026-05-31] LEON AI v4 vor dem Refactoring

**Typ:** Hinzugefügt / Geändert

### Was geändert wurde
- Passwort-Authentifizierung, Rate Limiting, Vision-Routen, PWA-Support, Token-Budgeting und das erste Live-Vorschau-Panel ergänzt.
- Produktions-Defaults verbessert und aggressives Service-Worker-Caching entfernt.

### Warum es wichtig ist
- Diese Version brachte den ersten vollständigen lokalen KI-Arbeitsbereich, bevor die modulare Architektur entstand.
