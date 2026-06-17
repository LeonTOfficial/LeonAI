# Sicherheit von LEON AI

![Sicherheit](https://img.shields.io/badge/Sicherheit-Local--First-17a673?style=for-the-badge)
![Secrets](https://img.shields.io/badge/Secrets-.env-5357ff?style=for-the-badge)
![Netzwerk](https://img.shields.io/badge/Standard-127.0.0.1-111827?style=for-the-badge)

## Ziel des Sicherheitsmodells

LEON AI ist als lokaler persönlicher KI-Arbeitsbereich gedacht. Das Sicherheitsmodell soll private Daten auf dem Gerät behalten, versehentliche Veröffentlichungen vermeiden und Fehler nachvollziehbar machen.

| Prinzip | Bedeutung |
| --- | --- |
| Lokal zuerst | Chats, Einstellungen, Logs, Artefakte und Backups liegen lokal auf dem Gerät. |
| Keine stille Cloud | Die App lädt lokale Daten nicht ungefragt in eine Cloud hoch. |
| Lokaler Zugriff | Standardmäßig läuft LEON AI auf `127.0.0.1`. |
| Secrets in `.env` | Passwörter, API-Schlüssel und `SECRET_KEY` gehören nicht ins Repository. |
| Fehler mit Request-ID | Nutzer sehen sichere Fehlermeldungen, Details bleiben im lokalen Log. |

## Wo liegen Daten?

| Datentyp | Standardort | Öffentlich? |
| --- | --- | --- |
| Chats und Nachrichten | `data/` SQLite-Datenbank | Nein |
| Artefakt-Versionen | `data/` SQLite-Datenbank | Nein |
| Logs | `data/logs/leon.log` | Nein |
| Backups | `backup/` | Nein |
| Profil und Setup | lokale Daten / `.env` | Nein |

## Wichtige Sicherheitsbereiche

| Bereich | Datei im Hauptprojekt | Aufgabe |
| --- | --- | --- |
| Authentifizierung | `routes/auth.py` | Login, Logout und Ersteinrichtung. |
| CSRF und Rate Limits | `utils/security.py` | Schutz für verändernde Anfragen und Login-Versuche. |
| Security Header | `routes/middleware.py` | CSP, Request-IDs, Origin-Prüfung und Header. |
| Fehlerabschirmung | `utils/errors.py` | Keine internen Stacktraces im Browser. |
| Logs | `utils/logging.py` | Strukturierte lokale Logs. |
| Backups | `services/backup_service.py` | Prüfsummen, Restore-Schutz und Sicherheitsbackup vor Restore. |
| Vorschau | `static/js/artifacts.js` | iFrame-Vorschau, Pyodide und Terminal-/Fehlerbrücke. |

## API-Schlüssel und Passwörter

Secrets gehören immer in `.env` und niemals in GitHub:

```env
LEON_PASSWORD=ein-lokales-passwort
SECRET_KEY=ein-langer-zufaelliger-wert
```

Vor jedem Release sollte geprüft werden, dass diese Dinge nicht gestaged sind:

- `.env`
- `data/`
- `backup/`
- `venv/`
- Datenbanken
- Logs
- Tokens oder API-Schlüssel

## Artifacts und Vorschau

Die Vorschau ist der sensibelste Bereich, weil dort KI-generierter HTML-, CSS-, JavaScript- und Python-Code angezeigt werden kann.

| Risiko | Umgang damit |
| --- | --- |
| Generierter JavaScript-Code | Nur in der Vorschau ausführen und nie mit Secrets füttern. |
| Relative Asset-Pfade | Werden neutralisiert, damit keine unnötigen lokalen Anfragen entstehen. |
| Pyodide | Läuft im Browser und nicht direkt als System-Python. |
| Externe Bibliotheken | Kernfunktionen sollen auch bei CDN-Problemen kontrolliert bleiben. |
| CSP/iFrame | Änderungen daran müssen vorsichtig getestet werden. |

## Fehler und Logs verstehen

LEON AI trennt sichtbare Fehlermeldungen von technischen Details.

| Ebene | Sichtbar für Nutzer | Lokal gespeichert |
| --- | --- | --- |
| Browser/API | Kurze Meldung und Request-ID | Keine Stacktraces |
| Lokales Log | Technische Details | `data/logs/leon.log` |
| Debugging | Request-ID verbindet Browser und Log | Nur lokal teilen, wenn sicher |

## Sicherheitslücken melden

Bitte Sicherheitslücken nicht mit Exploit-Details öffentlich posten.

Empfohlener Ablauf:

1. GitHub Security Advisories nutzen, falls verfügbar.
2. Sonst eine minimale öffentliche Issue öffnen: `Security contact requested`.
3. Keine Passwörter, API-Schlüssel, Tokens, privaten Logs oder Exploit-Payloads posten.
4. Details erst privat teilen.

## Was LEON AI nicht behauptet

| Punkt | Erklärung |
| --- | --- |
| Kein öffentliches SaaS-Hardening | LEON AI ist primär ein lokaler persönlicher Arbeitsbereich. |
| Keine Garantie für generierten Code | KI-Code muss geprüft werden. |
| Kein Schutz bei falscher Netzwerkfreigabe | Wer `HOST=0.0.0.0` setzt, muss das Netzwerk selbst absichern. |
| Keine Rettung geleakter Secrets | Geleakte Schlüssel müssen sofort rotiert werden. |
