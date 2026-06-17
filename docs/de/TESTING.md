# Tests und Qualitätssicherung

![Tests](https://img.shields.io/badge/Tests-55%20Python%20%2B%20Browser--QA-17a673?style=for-the-badge)
![CI](https://img.shields.io/badge/GitHub%20Actions-aktiv-5357ff?style=for-the-badge)
![Browser](https://img.shields.io/badge/Playwright-Chromium-111827?style=for-the-badge)

## Kurzbefehle

Im Hauptprojekt werden die Tests so ausgeführt:

```bash
./venv/bin/python -m unittest discover -s tests -q
python scripts/leon_doctor.py
python scripts/leon_doctor.py --run-tests
git diff --check
```

JavaScript und Browser-QA:

```bash
npm install
npm run check:js
npx playwright install chromium
npm run test:browser
```

## Was wird getestet?

| Bereich | Zweck |
| --- | --- |
| Backend | Flask-Routen, Services, Datenbank, Backups und Fehlerbehandlung. |
| Authentifizierung | Login, First Setup, Sessions, CSRF und geschützte Routen. |
| Chat | Räume, Nachrichten, Branching, Auto-Titel und Favoriten. |
| Artifacts | Speichern, Deduplizieren, Löschen, Export und Vorschau-Verträge. |
| Rich Rendering | Farbtags, Mermaid, Chart.js und Codeblöcke. |
| Dashboard | Metriken, Tokens, Privacy Center, Health Center und Debug Center. |
| Sicherheit | CSRF, Origin-Checks, sichere Fehlerantworten und private Runtime-Dateien. |
| Browser-QA | Echte Oberfläche im Chromium-Browser mit festen Testdaten. |

## GitHub Actions

Das Hauptrepo nutzt GitHub Actions für automatische Prüfungen bei Push und Pull Request.

| Schritt | Werkzeug | Warum? |
| --- | --- | --- |
| Python 3.11 / 3.12 | `actions/setup-python` | Prüft unterstützte Python-Versionen. |
| Release Doctor | `scripts/leon_doctor.py` | Prüft Doku, CI, Pflichtdateien und Git-Sicherheit. |
| Python-Tests | `unittest` | Prüft Backend und Verträge. |
| JavaScript-Syntax | `npm run check:js` | Findet kaputte JS-Dateien früh. |
| Browser-QA | Playwright Chromium | Prüft echte Screens und Rendering. |

Python 3.9 wird bewusst nicht verwendet, weil LEON AI moderne Python-Syntax wie `str | None` nutzt.

## Browser-QA

Die Browser-Tests brauchen keine echte Ollama-Antwort. Sie verwenden feste Testdaten und prüfen sichtbar:

- Login oder First Setup
- Dashboard ohne JavaScript-Fehler
- Chat-Shell mit Sidebar, Eingabe und Status
- Farbtags im Chat
- Chart.js Canvas
- Mermaid SVG
- Artifacts-iFrame mit einfachem HTML

## Manuelle Prüfungen

Vor einem größeren Release sollte zusätzlich manuell geprüft werden:

| Prüfung | Erwartung |
| --- | --- |
| macOS Start | `Starten.command` startet App und zeigt Status. |
| Windows Start | `Starten.ps1` erstellt venv, installiert Abhängigkeiten und startet App. |
| Linux Start | `start.sh` funktioniert in einer normalen Shell. |
| Ollama offline | App zeigt kontrollierte Warnung statt Absturz. |
| Vorschau | HTML/CSS/JS wird sichtbar im Panel angezeigt. |
| Dashboard | Charts, Tokens, Privacy und Logs laden. |
| GitHub README | Bilder, Links und Installationsschritte werden korrekt angezeigt. |

## Erwartete Test-Logs

Einige Tests lösen absichtlich Fehler aus, um Sicherheitsverhalten zu prüfen.

| Log | Warum es erscheinen kann |
| --- | --- |
| `403` | CSRF- und Origin-Schutz werden absichtlich getestet. |
| `500` | Fehlerabschirmung wird absichtlich getestet. |
| Request-ID | Verbindet sichere Browsermeldung mit lokalem Log. |

Ein Testlauf gilt als erfolgreich, wenn am Ende `OK` erscheint.
