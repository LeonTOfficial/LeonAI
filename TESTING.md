# LEON AI Testing

## Schnelltest

```bash
./venv/bin/python -m unittest discover -s tests -v
```

## Was aktuell abgedeckt ist

- UI-Flows ohne neue Abhaengigkeit: Login-Seite, Chat-Shell, neuer Chat, leere Nachrichten
- UI-Flows: Branching-Daten, aktiver Ast, Artifact-Versionen und Preview-Dropdown-API
- UI-Vertraege: Pyodide, Mermaid, Chart.js und Artifact-Controls sind im Frontend verdrahtet
- Datenbank-Migration fuer `messages.parent_id`
- Backfill alter linearer Chat-Verlaeufe
- Branching-Kontext: nur der aktive Ast wird ans Modell gegeben
- Neue leere Chats: neue Nachricht wird nicht doppelt an Ollama geschickt
- Auto-Titel: nutzt `llama3.2:1b`
- Fehlerantworten: Request-ID sichtbar, interne Details bleiben verborgen
- Fehlerdiagnose: Frontend-Fehler, Dashboard-Fehler und Streams zeigen/transportieren Request-IDs
- Security: fremde Origins werden bei schreibenden Requests geblockt
- Security: angemeldete POST/PATCH/DELETE-Requests brauchen einen CSRF-Token
- Frontend: Chat, Dashboard und Streaming-Requests senden den CSRF-Token mit
- Rich Chat: Mermaid, Chart.js und Farbtags sind im Renderer verankert
- Artifact Studio: Tabs, Terminal, Fehlerliste, mehrere Artefakte, HTML-/ZIP-Download
- Artifact Studio: persistenter Versionsverlauf mit SQLite-Dedupe und API-Sync
- Artifact Studio: einzelne gespeicherte Versionen loeschen und alle Versionen als ZIP exportieren
- Health Center: Datenbank-, Log-, Backup- und Ollama-Checks
- Privacy Center: Datenzaehlung und geschuetztes Loeschen sensibler Bereiche
- Backup-Sicherheit: SQLite-Backup, SHA-256-Manifest und Integritaetspruefung
- Privacy: Backup-Manifeste werden beim Loeschen mit entfernt

## Naechste sinnvolle Teststufe

- Echte Browser-/UI-Tests mit Playwright, sobald die Abhaengigkeit installiert ist: Login, neuer Chat, Branching, Artifact-Vorschau
- Browser-/UI-Test: Pyodide laedt und fuehrt Python im Artefakt aus
- Browser-/UI-Test: Mermaid und Charts rendern sichtbar im Chat
- Browser-/UI-Test: Avatar bleibt in Chat und Dashboard gleich
- Sicherheits-Test: Upload-Grenzen und Artifact-Sandbox im Browser pruefen
