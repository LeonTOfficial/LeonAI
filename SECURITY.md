# LEON AI Security

![Security](https://img.shields.io/badge/security-local--first-17a673?style=for-the-badge)
![Secrets](https://img.shields.io/badge/secrets-.env%20only-5357ff?style=for-the-badge)
![Network](https://img.shields.io/badge/default%20host-127.0.0.1-111827?style=for-the-badge)
![Reporting](https://img.shields.io/badge/reporting-private%20first-d99b18?style=for-the-badge)

### 1. Security Goal

LEON AI is designed as a **local-first personal AI workspace**. The goal is to keep private user data on the user’s own device, reduce accidental exposure, and make security behavior easy to inspect.

| Principle | What LEON AI does |
| --- | --- |
| Local-first data | Chats, settings, logs, artifacts, and backups are stored locally on the user’s device. |
| No silent cloud sync | LEON AI does not upload local app data to a cloud service without the user explicitly configuring or triggering external services. |
| Local network by default | The Flask server defaults to `HOST=127.0.0.1`, so it is reachable only from the same machine. |
| Explicit external model calls | Ollama is used locally by default through `http://localhost:11434`. Other API providers must be configured explicitly by the user. |
| Secrets stay local | API keys and passwords belong in `.env`, never in Git. |

### 2. Security Architecture Overview

| Area | Implementation | Evidence in the repository |
| --- | --- | --- |
| Configuration | Centralized defaults for host, port, auth, rate limit, paths, and Ollama model settings | `config.py` |
| Authentication | Login, logout, and first-time setup with a user-defined password and first name | `routes/auth.py` |
| Password and request protection | Password checks, CSRF tokens, login decorator, rate-limit helpers, origin validation | `utils/security.py` |
| Security headers | Content Security Policy, frame restrictions, referrer policy, permissions policy, request IDs | `routes/middleware.py` |
| Error shielding | Browser responses avoid internal stack traces and expose request IDs for debugging | `utils/errors.py` |
| Logging | Structured rotating logs in `data/logs/leon.log` | `utils/logging.py` |
| Local database | SQLite schema, migrations, chat branching, artifacts, and profile data | `models/database.py` |
| Backups | Local SQLite backup flow with manifest/integrity metadata | `services/backup_service.py` |
| Privacy tools | Local data counting and protected purge operations | `utils/privacy.py` |
| Health checks | Local checks for database, logs, backups, and Ollama availability | `utils/system_health.py` |
| Artifact preview | Preview iframe, neutralized relative asset paths, browser-side Python/Pyodide wiring | `static/js/artifacts.js` |
| Rich chat rendering | DOMPurify, colored tags, Mermaid, Chart.js rendering contracts | `static/js/chat.js` |
| Git safety | Local runtime data, backups, logs, virtual environments, and secrets are ignored | `.gitignore` |

### 3. Data Sovereignty

| Data type | Default location | Cloud transfer by default? | Notes |
| --- | --- | ---: | --- |
| Chats and messages | `data/` SQLite database | No | Stored locally on the device. |
| Artifacts and preview history | `data/` SQLite database | No | Used for local preview/version history. |
| Logs | `data/logs/leon.log` | No | Useful for debugging, should not be published. |
| Backups | `backup/` | No | Local backup files and manifests. |
| Profile/setup data | Local database and `.env` settings | No | First name/password setup remains local. |
| Model requests | Local Ollama endpoint by default | No external cloud by default | External model providers require explicit configuration. |

LEON AI is built for private local usage. If the user changes `HOST` to `0.0.0.0`, the app may become reachable from other devices in the network. That should only be done intentionally and inside a trusted network.

### 4. API Keys And Secrets

| Secret | Recommended storage | Repository status |
| --- | --- | --- |
| `LEON_PASSWORD` | `.env` | Must not be committed |
| `SECRET_KEY` | `.env` | Must not be committed |
| External LLM/API keys | `.env` | Must not be committed |
| Local databases | `data/` | Must not be committed |
| Logs and backups | `data/logs/`, `backup/` | Must not be committed |

Security rules:

- Keep `.env` local.
- Use long random values for `SECRET_KEY`.
- Rotate leaked keys immediately.
- Never paste GitHub tokens, API keys, passwords, logs, or `.env` content into public Issues.
- Before publishing a release, check that `.env`, `data/`, `backup/`, `venv/`, databases, and logs are not staged for Git.

### 5. Dependencies

LEON AI uses a small Python dependency surface:

| Dependency | Purpose |
| --- | --- |
| `Flask>=3.0.0` | Local web backend |
| `requests>=2.31.0` | HTTP communication with local/external model endpoints |
| `python-dotenv>=1.0.0` | Local `.env` configuration |
| `pyopenssl>=23.0.0` | TLS/crypto support where needed |

Dependency policy:

- Keep dependencies minimal and understandable.
- Prefer well-known maintained libraries.
- Install dependencies inside a local virtual environment.
- Review dependency changes before release.
- Do not commit `venv/` or generated dependency folders.

### 6. Artifacts, Preview Sandbox, And CSP

The Artifacts panel is the most security-sensitive area because it previews AI-generated HTML, CSS, JavaScript, and browser-side Python experiments.

| Area | Current approach | Security note |
| --- | --- | --- |
| Preview isolation | Generated pages are rendered in the Artifacts preview instead of being mixed directly into the main chat DOM. | Preview code should be treated as untrusted generated content. |
| iframe boundary | The preview flow is handled in `static/js/artifacts.js`. | Any sandbox or iframe-policy change should be reviewed carefully. |
| JavaScript execution | Generated JavaScript may run inside the preview context. | Do not paste secrets or private data into generated preview code. |
| Pyodide | Python experiments run in the browser through Pyodide. | This is useful for learning and demos, but it is not a replacement for professional isolation. |
| External CDNs | Some rich preview features may depend on trusted CDNs. | Network failures should not break the core local chat workflow. |
| CSP trade-offs | The app uses a Content Security Policy in `routes/middleware.py`. | Rich previews may require allowances such as inline styles/scripts, `blob:`, `data:`, or trusted CDNs. Tightening CSP should be tested against Artifacts. |

### 7. Logs And Debug Data

Logs are local and useful for debugging, but they can contain sensitive context such as prompts, local paths, request IDs, or error details.

| Log area | Location | Guidance |
| --- | --- | --- |
| Runtime log | `data/logs/leon.log` | Keep local; do not commit or publish full logs. |
| Terminal activity | Controlled through `LEON_TERMINAL_ACTIVITY` | Useful for local status output. |
| Technical log level | Controlled through `LEON_TERMINAL_LOG_LEVEL` | Keep noisy details out of normal terminal output. |
| Error reports | GitHub Issues or private security report | Share only minimal, redacted excerpts. |

### 8. Network Exposure

By default, LEON AI is intended to run on `127.0.0.1`, meaning only the same machine can access it. Setting `HOST=0.0.0.0` can expose the app to other devices on the network and should only be done intentionally in a trusted environment.

### 9. Vulnerability Reporting

Please report security vulnerabilities **privately first**.

| Do | Do not |
| --- | --- |
| Use GitHub’s private vulnerability reporting / Security Advisories if available. | Do not post exploit details in a public Issue. |
| If private reporting is unavailable, contact Leon privately through GitHub and request a secure channel. | Do not include API keys, passwords, tokens, private logs, or personal files in a public message. |
| Include clear reproduction steps, affected version/commit, screenshots if safe, and impact. | Do not run destructive tests against other people’s systems. |

Suggested report structure:

```text
Title: Short vulnerability summary
Affected version/commit:
Environment: macOS / Windows / Linux, Python version, browser
Impact:
Reproduction steps:
Expected behavior:
Actual behavior:
Suggested fix, if known:
```

If the issue is urgent and no private channel is available, open a minimal public Issue that says only: **“Security contact requested”**. Do not include technical exploit details publicly.

### 10. What LEON AI Does Not Claim

| Non-goal | Explanation |
| --- | --- |
| Public multi-user cloud hardening | LEON AI is built primarily as a local personal workspace, not as a hosted enterprise SaaS. |
| Perfect safety for generated code | AI-generated code can be wrong or unsafe and must be reviewed before real use. |
| Automatic protection for custom network exposure | If `HOST=0.0.0.0` is enabled, the user is responsible for network safety. |
| Secret recovery after leaks | Leaked credentials must be rotated at the provider immediately. |

### 11. Release Security Model

The public repository is meant to contain source code, documentation, tests, and screenshots, but not private runtime data. A safe release therefore keeps a clear boundary between project files and local user data.

| Release area | Security meaning |
| --- | --- |
| Automated tests | The test suite described in [`TESTING.md`](TESTING.md) documents the expected behavior for auth, CSRF, errors, privacy tools, backups, and rich frontend contracts. |
| Secrets | `.env`, passwords, API keys, tokens, local databases, logs, and backups are runtime data and stay outside Git. |
| Request protection | Changes in `routes/middleware.py` and `utils/security.py` are security-sensitive because they affect headers, CSRF, origin checks, sessions, and login behavior. |
| Preview isolation | Changes in `static/js/artifacts.js` are security-sensitive because they affect how generated HTML, JavaScript, Python, and iframe previews behave. |
| Public communication | Security-sensitive findings should use private reporting first, while normal bugs and questions can be discussed through GitHub Issues. |
