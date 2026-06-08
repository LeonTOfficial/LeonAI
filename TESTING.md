# LEON AI Testing

This file documents how LEON AI is checked before a GitHub release.

## Quick Command

```bash
./venv/bin/python -m unittest discover -s tests -q
```

For more detail:

```bash
./venv/bin/python -m unittest discover -s tests -v
```

Frontend syntax check:

```bash
node --check static/js/api.js
node --check static/js/ui.js
node --check static/js/artifacts.js
node --check static/js/chat.js
```

## What Is Covered

| Area | What is checked | Main evidence |
| --- | --- | --- |
| Authentication | Login, protected pages, first setup | `tests/test_core.py`, `routes/auth.py` |
| Security | CSRF, origin checks, safe error messages | `tests/test_core.py`, `utils/security.py`, `routes/middleware.py`, `utils/errors.py` |
| Chat rooms | Create, load, delete, pin/favorite-style state | `tests/test_core.py`, `routes/api.py`, `services/room_service.py` |
| Branching | Message parent IDs, active path, branch context | `tests/test_core.py`, `models/database.py`, `services/chat_service.py` |
| Ollama contracts | Auto-title model and chat payload structure | `tests/test_core.py`, `services/ollama_service.py`, `config.py` |
| Artifacts | Preview controls, version history, delete, ZIP export | `tests/test_core.py`, `services/artifact_service.py`, `static/js/artifacts.js` |
| Rich chat | Mermaid, Chart.js, colored tags | `tests/test_core.py`, `static/js/chat.js` |
| Pyodide | Browser Python loader contract and error handling | `tests/test_core.py`, `static/js/artifacts.js` |
| Dashboard | Metrics, privacy center, debug center, token explanation | `tests/test_core.py`, `templates/dashboard.html` |
| Backups | SQLite backup, manifest and integrity checks | `tests/test_core.py`, `services/backup_service.py` |
| Privacy tools | Counting and protected deletion of local data | `tests/test_core.py`, `utils/privacy.py` |
| Release docs | README, security notes and ignored private files | `tests/test_core.py`, `README.md`, `README_SICHERHEIT.txt`, `.gitignore` |

## Manual QA Checklist

Before publishing a release, run through this:

1. Start the app with `./Starten.command`.
2. Open `http://127.0.0.1:5001`.
3. Log in or complete First Setup on a fresh data directory.
4. Send a normal German chat message and confirm the answer stays in German.
5. Ask for a simple HTML page and confirm the preview panel renders visible content.
6. Click `Code`, `Terminal`, and `Fehler` inside the preview panel.
7. Click `Aktualisieren` in the preview panel.
8. Ask for a Mermaid diagram and confirm it renders in chat.
9. Ask for a simple Chart.js/bar-chart block and confirm it renders in chat.
10. Ask for colored text such as `[rot]Beispiel[/rot]` and confirm the color appears.
11. Open the dashboard and confirm metrics, token explanation, privacy center and debug center.
12. Check `data/logs/leon.log` for unexpected `ERROR` lines.

## Known Expected Test Logs

Some tests intentionally trigger 403 and 500 responses to prove that security and error shielding work. During the unit test run, those log lines can appear in the terminal or `leon.log`. They are expected if the final unittest result is `OK`.

Examples:

- `Fehler 403` for CSRF/origin checks.
- `Fehler 500` for the deliberate hidden-error test.
- `secret internal detail` may appear in the local log during the test, but must not be returned to the browser response.

## Release Rule

A release is only considered ready when:

- Unit tests pass.
- JS syntax checks pass.
- The live preview renders visible HTML in the browser.
- `.env`, `data/`, `backup/`, `venv/`, databases and logs are not staged for Git.
- `README.md`, `README_SICHERHEIT.txt`, `STRUKTUR.md` and `TESTING.md` describe the current state.
