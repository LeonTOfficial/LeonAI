# LEON AI Testing

![Tests](https://img.shields.io/badge/tests-48%20automated-17a673?style=for-the-badge)
![Backend](https://img.shields.io/badge/backend-Flask-111827?style=for-the-badge)
![Frontend](https://img.shields.io/badge/frontend-vanilla%20JS-5357ff?style=for-the-badge)
![QA](https://img.shields.io/badge/QA-release%20checklist-d99b18?style=for-the-badge)

### 1. Quick Test Commands

Run the full automated test suite:

```bash
./venv/bin/python -m unittest discover -s tests -q
```

Run the release readiness doctor:

```bash
python scripts/leon_doctor.py
```

Run the doctor and the Python tests together:

```bash
python scripts/leon_doctor.py --run-tests
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
| Release doctor | `python scripts/leon_doctor.py` | Checks required files, public docs, CI wiring, and accidental runtime-data tracking. |
| Backend tests | `python -m unittest discover -s tests -q` | Verifies Flask routes, services, security, database, artifacts, and UI contracts. |
| Frontend syntax | `node --check static/js/*.js` | Catches JavaScript syntax breakage before release. |

The CI matrix intentionally uses **Python 3.11 and 3.12**. Python 3.9 is not included because the project uses modern Python syntax such as `str | None`, which requires Python 3.10 or newer.

### 3. Current Automated Coverage

The current automated suite covers **48 tests** across backend behavior, frontend contracts, security controls, artifacts, privacy tooling, backups, and UI flow expectations.

| Test area | What is checked | Main evidence |
| --- | --- | --- |
| Database migrations | Parent IDs, artifact version tables, schema compatibility | `tests/test_core.py`, `models/database.py` |
| Authentication | Login, protected pages, first setup, session state | `tests/test_core.py`, `tests/test_ui_flows.py`, `routes/auth.py` |
| CSRF and origin protection | Mutating requests require valid CSRF and trusted origins | `tests/test_core.py`, `utils/security.py`, `routes/middleware.py` |
| Error shielding | Internal API/chat error details stay out of browser responses, request IDs remain visible | `tests/test_core.py`, `utils/errors.py`, `routes/api.py`, `routes/chat.py` |
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
| Release readiness | Doctor script validates docs, CI, required files, and ignored runtime data | `tests/test_core.py`, `scripts/leon_doctor.py`, `.github/workflows/test.yml` |

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

### 5. Missing Tests To Add Next

The current test suite is useful, but it does not claim complete coverage. The next practical additions should focus on the highest-risk flows.

| Missing area | Why it matters |
| --- | --- |
| Browser-level preview tests | Proves that generated HTML/CSS/JS actually renders in a real browser. |
| Artifact security regression tests | Protects iframe, CSP, relative asset handling, and generated-code boundaries. |
| More migration tests | Ensures older local databases upgrade cleanly. |
| Accessibility checks | Helps keep login, chat, dashboard, and artifact controls usable. |
| Larger end-to-end setup test | Verifies a fresh clone, first setup, login, chat, and preview flow together. |

### 6. Functional Tests

| Function | Expected behavior | Failure mode checked |
| --- | --- | --- |
| Module initialization | Routes, services, database tables, and templates load correctly | Missing tables or broken imports fail tests |
| Flask backend stability | Local test client handles login, API calls, mutations, and dashboard routes | 403/500 handling stays controlled |
| AI interface handling | Ollama availability, model listing, auto-title payloads, timeout/error paths | Offline Ollama returns safe warnings |
| Artifact system | Generated HTML/CSS/JS/Python snippets are saved, versioned, previewed, and exportable | Duplicate versions are deduped; deleted versions are removed |
| Chat branching | Editing from older messages can create a new path without corrupting existing history | Active branch path is built from selected leaf |
| Backup system | Backups include integrity metadata and can detect modified files | Modified backup verification fails safely |

### 7. UI/UX Tests

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

### 8. Error Handling Tests

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

### 9. Manual QA Story

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

### 10. Known Expected Test Logs

Some automated tests intentionally trigger failures to prove security and error shielding work. These log lines can appear during testing and are expected if the final unittest result is `OK`.

| Expected test log | Why it appears |
| --- | --- |
| `403` | CSRF and origin-protection tests intentionally send invalid requests. |
| `500` | Hidden-error tests intentionally trigger backend errors. |
| Internal test detail in local log | The local log may contain debug information, but the browser response must not expose it. |

### 11. Release Readiness

LEON AI is considered release-ready when the technical tests and the product story agree with each other: the automated suite passes, the JavaScript files parse correctly, the preview panel works in a browser, and the documentation describes the current behavior honestly.

| Release signal | Meaning |
| --- | --- |
| Unit tests pass | Backend behavior, security contracts, artifacts, privacy tools, backups, and UI contracts match the expected model. |
| JavaScript checks pass | The frontend modules can load without syntax-level breakage. |
| Manual preview works | Generated HTML/CSS/JS, Mermaid, Chart.js, Pyodide, and color tags are usable in the real interface. |
| Documentation is current | README, architecture, security, and testing files explain the same product that users actually download. |
| Private files stay local | `.env`, `data/`, `backup/`, `venv/`, databases, logs, and tokens stay out of the public repository. |
