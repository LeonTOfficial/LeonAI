# Changelog

All notable public changes to LEON AI are documented here.

This file is the public release history. [`UPDATES.md`](UPDATES.md) remains an internal development log with more detailed notes about implementation decisions, logs, and debugging.

## Unreleased

### Changed
- Main repository documentation is now English-first.
- Public release history moved to `CHANGELOG.md`.
- `UPDATES.md` remains available as an internal developer log.

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
