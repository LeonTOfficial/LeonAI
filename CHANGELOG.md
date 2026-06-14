# Changelog

All notable public changes to LEON AI are documented here.

This file is the public release history. [`UPDATES.md`](UPDATES.md) remains an internal development log with more detailed notes about implementation decisions, logs, and debugging.

## Unreleased

### Added
- Backup inventory and restore flow for the dashboard.
- Restore safety checks: checksum verification, filename confirmation, SQLite quick check, and automatic pre-restore backup.

### Changed
- Main repository documentation is now English-first.
- Public release history moved to `CHANGELOG.md`.
- `UPDATES.md` remains available as an internal developer log.
- API and streaming errors now return safe user-facing messages with request IDs while internal details stay in local logs.
- CI is now focused on one workflow: tests, JavaScript syntax checks, and release readiness checks.

### Security
- Added a shared JSON error helper for API routes, middleware, and chat streams.
- Expanded automated coverage for hidden internal API errors.
- Added `scripts/leon_doctor.py` to detect missing public files, broken local doc links, CI drift, and accidentally tracked runtime data.

## v1.0.0

### Added
- Local AI chat workspace powered by Flask, SQLite, and Ollama.
- Room-based chat history with messages, favorites, pinning, auto titles, and branching support.
- Live Artifacts panel for generated HTML, CSS, JavaScript, Tailwind-style layouts, and Python snippets.
- Browser-side Python experiments through Pyodide.
- Mermaid diagrams and Chart.js charts rendered directly in chat.
- Vision image upload support when a compatible vision model is installed.
- First setup flow with local password and profile name.
- Privacy/dashboard area with activity, token, backup, log, and health information.
- Local SQLite backups with integrity metadata.
- GitHub Actions workflow for Python 3.11/3.12 tests and JavaScript syntax checks.

### Documentation
- Added public README with screenshots, installation instructions, storage requirements, and license summary.
- Added security, testing, architecture, contribution, and update documentation.

### Notes
- LEON AI is proprietary source-available software.
- Private use of the official app/demo is allowed without prior permission.
- Copying, modifying, self-hosting, redistributing, rebranding, publishing, or commercial use requires prior written permission from Leon.
