# LEON AI Updates

![Changelog](https://img.shields.io/badge/changelog-active-5357ff?style=for-the-badge)
![Logs](https://img.shields.io/badge/logs-structured-111827?style=for-the-badge)
![CI](https://img.shields.io/badge/GitHub%20Actions-ready-17a673?style=for-the-badge)

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
