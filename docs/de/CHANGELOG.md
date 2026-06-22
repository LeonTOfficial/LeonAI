# Änderungsverlauf

Dies ist die deutsche Zusammenfassung der öffentlichen Änderungen. Die englische Release-Historie liegt im Repository-Root: [`CHANGELOG.md`](../../CHANGELOG.md).

## Unreleased

### Hinzugefügt

- Browser-QA mit Playwright für Login/Setup, Dashboard, Chat-Shell, Farbtags, Chart.js, Mermaid und Artifacts-Vorschau.
- Windows-Starter `Starten.ps1`.
- Linux/macOS-Shell-Starter `start.sh`.
- GitHub Issue Templates für Bugs, Features, Feedback und Security Contact.
- Pull-Request-Vorlage mit Hinweis auf Source-Available-Lizenz.
- Öffentliche Roadmap im Hauptrepo.
- Vorbereitung für den deutschen Doku-Bereich `docs/de/`.
- Öffentliche Fehlerhilfe `TROUBLESHOOTING.md` plus deutsche Spiegeldatei für häufige Setup-, Vorschau-, Ollama-, Log-, Request-ID- und CI-Probleme.
- Anfängerfreundliche `GETTING_STARTED.md` und feedbackorientierte `FEEDBACK.md`, jeweils mit deutscher Spiegeldatei.
- Datensparsame Diagnose-API und Dashboard-Aktion zum Kopieren von Support-Informationen.
- Artifacts-Vorschau-Selbsttest für iframe-Rendering, HTML/CSS/JS-Ausführung, Canvas-Ausgabe und Terminal-Bridge-Logs.
- Dependabot-Konfiguration für Python-, JavaScript- und GitHub-Actions-Abhängigkeiten.

### Geändert

- Hauptrepo ist Englisch-first.
- Deutsche Dokumentation wird im Ordner `docs/de/` gepflegt.
- README erklärt nun einen empfohlenen Startweg pro Plattform.
- README verlinkt eine eigene Fehlerhilfe, statt häufige Lösungen im Installationsabschnitt zu verstecken.
- Dashboard zeigt die aktuelle App-Version über die Diagnose-Zusammenfassung.
- CI prüft zusätzlich Browser-QA.

## v1.0.0

### Hinzugefügt

- Lokaler KI-Chat mit Flask, SQLite und Ollama.
- Räume, Nachrichten, Favoriten, Pinning, Auto-Titel und Branching.
- Live Artifacts für HTML, CSS, JavaScript, Tailwind-Layouts und Python-Snippets.
- Pyodide für Python-Experimente im Browser.
- Mermaid-Diagramme und Chart.js-Charts direkt im Chat.
- Vision-Bild-Uploads mit passendem Vision-Modell.
- First Setup mit lokalem Passwort und Vornamen.
- Dashboard für Aktivität, Tokens, Backups, Logs, Health und Privacy.
- Lokale SQLite-Backups mit Integritätsdaten.
- GitHub Actions für Tests und Qualitätschecks.

### Hinweis

LEON AI ist proprietäre Source-Available-Software. Private Nutzung der offiziellen App/Demo ist erlaubt. Kopieren, Verändern, Selbsthosten, Weiterverbreiten, Rebranding, Veröffentlichen oder kommerzielle Nutzung des Quellcodes benötigt vorherige schriftliche Genehmigung von Leon.
