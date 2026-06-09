# LEON AI Security

![Security](https://img.shields.io/badge/security-local--first-17a673?style=for-the-badge)
![Secrets](https://img.shields.io/badge/secrets-.env%20only-5357ff?style=for-the-badge)
![Network](https://img.shields.io/badge/default%20host-127.0.0.1-111827?style=for-the-badge)
![Reporting](https://img.shields.io/badge/reporting-private%20first-d99b18?style=for-the-badge)

> German version below.
> Deutsche Version weiter unten.

## English Version

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

### 6. Vulnerability Reporting

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

### 7. What LEON AI Does Not Claim

| Non-goal | Explanation |
| --- | --- |
| Public multi-user cloud hardening | LEON AI is built primarily as a local personal workspace, not as a hosted enterprise SaaS. |
| Perfect safety for generated code | AI-generated code can be wrong or unsafe and must be reviewed before real use. |
| Automatic protection for custom network exposure | If `HOST=0.0.0.0` is enabled, the user is responsible for network safety. |
| Secret recovery after leaks | Leaked credentials must be rotated at the provider immediately. |

### 8. Release Security Checklist

Before publishing a release:

- Run the full test suite from [`TESTING.md`](TESTING.md).
- Confirm `.env` is not staged.
- Confirm `data/`, `backup/`, `venv/`, `*.db`, and `*.log` are not staged.
- Review `routes/middleware.py` for security-header changes.
- Review `utils/security.py` for auth/CSRF/origin changes.
- Review `static/js/artifacts.js` for preview/iframe behavior.
- Search the repository for accidental tokens or passwords.

---

## Deutsche Version

### 1. Sicherheitsziel

LEON AI ist als **lokaler, privater KI-Arbeitsbereich** konzipiert. Das Ziel ist, persönliche Nutzerdaten auf dem eigenen Gerät zu halten, unbeabsichtigte Veröffentlichungen zu vermeiden und sicherheitsrelevantes Verhalten nachvollziehbar zu dokumentieren.

| Prinzip | Was LEON AI macht |
| --- | --- |
| Lokale Datenhoheit | Chats, Einstellungen, Logs, Artifacts und Backups werden lokal auf dem Gerät des Nutzers gespeichert. |
| Keine ungefragte Cloud-Synchronisierung | LEON AI lädt lokale App-Daten nicht ungefragt in einen Cloud-Dienst hoch. |
| Lokales Netzwerk als Standard | Der Flask-Server nutzt standardmäßig `HOST=127.0.0.1` und ist damit nur vom selben Gerät erreichbar. |
| Bewusste externe Modellaufrufe | Standardmäßig wird Ollama lokal über `http://localhost:11434` genutzt. Andere Anbieter müssen bewusst eingerichtet werden. |
| Secrets bleiben lokal | API-Schlüssel und Passwörter gehören in `.env`, niemals in Git. |

### 2. Sicherheitsarchitektur im Überblick

| Bereich | Umsetzung | Beleg im Repository |
| --- | --- | --- |
| Konfiguration | Zentrale Standardwerte für Host, Port, Authentifizierung, Rate Limit, Pfade und Ollama-Modell | `config.py` |
| Authentifizierung | Login, Logout und Ersteinrichtung mit eigenem Passwort und Vornamen | `routes/auth.py` |
| Passwort- und Request-Schutz | Passwortprüfung, CSRF-Tokens, Login-Decorator, Rate-Limit-Helfer, Origin-Prüfung | `utils/security.py` |
| Security-Header | Content Security Policy, Frame-Einschränkungen, Referrer Policy, Permissions Policy, Request-IDs | `routes/middleware.py` |
| Fehlerabschirmung | Browser-Antworten zeigen keine internen Stacktraces, sondern nachvollziehbare Request-IDs | `utils/errors.py` |
| Logging | Strukturierte rotierende Logs in `data/logs/leon.log` | `utils/logging.py` |
| Lokale Datenbank | SQLite-Schema, Migrationen, Chat-Branching, Artifacts und Profildaten | `models/database.py` |
| Backups | Lokale SQLite-Backups mit Manifest- und Integritätsinformationen | `services/backup_service.py` |
| Datenschutz-Werkzeuge | Lokales Zählen und geschütztes Löschen von Datenbereichen | `utils/privacy.py` |
| Health Checks | Lokale Prüfung von Datenbank, Logs, Backups und Ollama-Erreichbarkeit | `utils/system_health.py` |
| Artifact-Vorschau | Vorschau-iframe, neutralisierte relative Asset-Pfade, Browser-Python/Pyodide-Anbindung | `static/js/artifacts.js` |
| Rich Chat Rendering | DOMPurify, Farbtags, Mermaid- und Chart.js-Rendering-Verträge | `static/js/chat.js` |
| Git-Schutz | Lokale Laufzeitdaten, Backups, Logs, virtuelle Umgebungen und Secrets werden ignoriert | `.gitignore` |

### 3. Daten-Souveränität

| Datentyp | Standard-Speicherort | Cloud-Übertragung standardmäßig? | Hinweise |
| --- | --- | ---: | --- |
| Chats und Nachrichten | SQLite-Datenbank in `data/` | Nein | Wird lokal auf dem Gerät gespeichert. |
| Artifacts und Vorschau-Verlauf | SQLite-Datenbank in `data/` | Nein | Dient lokalen Vorschau- und Versionsfunktionen. |
| Logs | `data/logs/leon.log` | Nein | Hilfreich für Debugging, gehört nicht auf GitHub. |
| Backups | `backup/` | Nein | Lokale Backup-Dateien und Manifeste. |
| Profil-/Setup-Daten | Lokale Datenbank und `.env`-Werte | Nein | Vorname und Passwort-Einrichtung bleiben lokal. |
| Modellanfragen | Standardmäßig lokaler Ollama-Endpunkt | Keine externe Cloud standardmäßig | Externe Modellanbieter müssen bewusst konfiguriert werden. |

LEON AI ist für private lokale Nutzung gebaut. Wenn `HOST` auf `0.0.0.0` gesetzt wird, kann die App im Netzwerk erreichbar werden. Das sollte nur bewusst und ausschließlich in vertrauenswürdigen Netzwerken passieren.

### 4. API-Schlüssel und Secrets

| Secret | Empfohlener Speicherort | Repository-Status |
| --- | --- | --- |
| `LEON_PASSWORD` | `.env` | Darf nicht committed werden |
| `SECRET_KEY` | `.env` | Darf nicht committed werden |
| Externe LLM-/API-Schlüssel | `.env` | Dürfen nicht committed werden |
| Lokale Datenbanken | `data/` | Dürfen nicht committed werden |
| Logs und Backups | `data/logs/`, `backup/` | Dürfen nicht committed werden |

Sicherheitsregeln:

- `.env` bleibt lokal.
- Für `SECRET_KEY` lange zufällige Werte verwenden.
- Veröffentlichte Schlüssel sofort widerrufen und ersetzen.
- Niemals GitHub-Tokens, API-Schlüssel, Passwörter, Logs oder `.env`-Inhalte in öffentliche Issues kopieren.
- Vor einem Release prüfen, dass `.env`, `data/`, `backup/`, `venv/`, Datenbanken und Logs nicht für Git vorgemerkt sind.

### 5. Abhängigkeiten

LEON AI hält die Python-Abhängigkeiten bewusst überschaubar:

| Abhängigkeit | Zweck |
| --- | --- |
| `Flask>=3.0.0` | Lokales Web-Backend |
| `requests>=2.31.0` | HTTP-Kommunikation mit lokalen/externen Modell-Endpunkten |
| `python-dotenv>=1.0.0` | Lokale `.env`-Konfiguration |
| `pyopenssl>=23.0.0` | TLS-/Krypto-Unterstützung, wo benötigt |

Regeln für Abhängigkeiten:

- Abhängigkeiten minimal und verständlich halten.
- Etablierte und gepflegte Bibliotheken bevorzugen.
- Installation in einer lokalen virtuellen Umgebung durchführen.
- Änderungen an Abhängigkeiten vor Releases prüfen.
- `venv/` und generierte Abhängigkeitsordner niemals committen.

### 6. Sicherheitslücken melden

Bitte melde Sicherheitslücken **zuerst privat**.

| Bitte tun | Bitte vermeiden |
| --- | --- |
| GitHubs private Vulnerability-Reporting-Funktion/Security Advisories verwenden, wenn verfügbar. | Keine Exploit-Details in ein öffentliches Issue schreiben. |
| Falls kein privater Meldeweg verfügbar ist, Leon privat über GitHub kontaktieren und um einen sicheren Kanal bitten. | Keine API-Schlüssel, Passwörter, Tokens, privaten Logs oder persönlichen Dateien öffentlich posten. |
| Klare Reproduktionsschritte, betroffene Version/Commit, sichere Screenshots und Auswirkungen nennen. | Keine destruktiven Tests gegen fremde Systeme ausführen. |

Empfohlene Struktur für eine Meldung:

```text
Titel: Kurze Zusammenfassung der Sicherheitslücke
Betroffene Version/Commit:
Umgebung: macOS / Windows / Linux, Python-Version, Browser
Auswirkung:
Reproduktionsschritte:
Erwartetes Verhalten:
Tatsächliches Verhalten:
Vorgeschlagene Lösung, falls bekannt:
```

Falls das Problem dringend ist und kein privater Kanal verfügbar ist, eröffne nur ein minimales öffentliches Issue mit dem Text: **„Security contact requested“**. Technische Exploit-Details gehören nicht in die Öffentlichkeit.

### 7. Was LEON AI nicht verspricht

| Kein Ziel | Erklärung |
| --- | --- |
| Gehärteter öffentlicher Multi-User-Cloud-Dienst | LEON AI ist primär ein lokaler persönlicher Arbeitsbereich, kein gehostetes Enterprise-SaaS. |
| Perfekte Sicherheit für generierten Code | KI-generierter Code kann falsch oder unsicher sein und muss vor echter Nutzung geprüft werden. |
| Automatischer Schutz bei eigener Netzwerkfreigabe | Wenn `HOST=0.0.0.0` aktiviert wird, ist der Nutzer für Netzwerksicherheit verantwortlich. |
| Wiederherstellung nach Secret-Leaks | Veröffentlichte Zugangsdaten müssen sofort beim jeweiligen Anbieter widerrufen werden. |

### 8. Sicherheits-Checkliste vor Releases

Vor einer Veröffentlichung:

- Die vollständige Test-Suite aus [`TESTING.md`](TESTING.md) ausführen.
- Prüfen, dass `.env` nicht für Git vorgemerkt ist.
- Prüfen, dass `data/`, `backup/`, `venv/`, `*.db` und `*.log` nicht vorgemerkt sind.
- Änderungen in `routes/middleware.py` auf Security-Header prüfen.
- Änderungen in `utils/security.py` auf Authentifizierung, CSRF und Origin-Checks prüfen.
- Änderungen in `static/js/artifacts.js` auf Vorschau-/iframe-Verhalten prüfen.
- Das Repository nach versehentlichen Tokens oder Passwörtern durchsuchen.
