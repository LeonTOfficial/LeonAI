# LEON AI – Änderungsprotokoll (Updates)

> Hier wird dokumentiert, **was wann geändert, hinzugefügt oder entfernt** wurde.
> Neue Einträge immer **oben** einfügen (neueste zuerst).

---

## Format für neue Einträge

```markdown
## [Datum] – Kurztitel

**Typ:** Hinzugefügt | Geändert | Entfernt | Fix | Refactoring

### Hinzugefügt
- …

### Geändert
- …

### Entfernt
- …

### Hinweise
- …
```

---

## Umgang mit Logs und Fehlerstruktur

Die Logs von LEON AI befinden sich in `data/logs/leon.log`. Ein Log-Eintrag (Fehler oder Info) ist immer in dieser Struktur aufgebaut:

1. **Zeitstempel:** Wann ist das Ereignis passiert? (z.B. `2026-06-10 12:34:56,789`)
2. **Loglevel:** Wie schwerwiegend ist das Ereignis? (`INFO`, `WARNING`, `ERROR`, `CRITICAL`)
3. **Modul:** In welcher Datei/Komponente ist es passiert? (z.B. `[utils.errors]`)
4. **Nachricht:** Was genau ist passiert? (z.B. `Ein unerwarteter Fehler ist aufgetreten`)

**Beispiel für einen Log-Eintrag:**
```text
2026-06-10 14:20:15,123 - ERROR - [utils.errors] - Ein unerwarteter Fehler ist aufgetreten: Database is locked.
```

**Bedeutung der Level:**
- `INFO`: Normale Vorgänge (App gestartet, Login erfolgreich).
- `WARNING`: Etwas ist nicht ideal, aber die App läuft weiter (z.B. Datei nicht gefunden).
- `ERROR`: Eine bestimmte Funktion ist fehlgeschlagen (z.B. Chatnachricht konnte nicht gespeichert werden).
- `CRITICAL`: Ein schweres Problem, das die App oft zum Absturz bringt.

## Fehler bei alten Python-Versionen

LEON AI ist auf aktuelle Python-Versionen optimiert (empfohlen: **Python 3.10 oder höher**). 
Wenn du versuchst, die App mit einer alten Python-Version (z.B. Python 3.8 oder 3.9) zu starten, können folgende Fehler auftreten:
- **Syntaxfehler durch neue Type-Hints**: Schreibweisen wie `str | None` anstelle von `Optional[str]` führen in alten Versionen zu Fehlern.
- **Inkompatible Abhängigkeiten**: Neuere Versionen in der `requirements.txt` setzen oft Python 3.10+ voraus.
- **Asyncio/Threading Probleme**: Bestimmte asynchrone Abläufe laufen auf veralteten Versionen nicht stabil.

**Lösung:** Wenn du direkt beim Starten in der Konsole Fehler siehst, überprüfe deine Python-Version mit `python --version` (oder `python3 --version`) und aktualisiere auf mindestens Python 3.10.

---

## [2026-06-04] – Log-Auswertung & 404-Fixes

**Typ:** Fix / Dokumentation

### Auswertung `data/logs/leon.log`

| Ergebnis | Details |
|----------|---------|
| ✅ Normal | App-Start, Login, Chat, Export, Dashboard – alles funktioniert |
| ⚠️ Behoben | ~40× HTTP 404 für `/leon-ai-profile.jpg` und `/leon-ai-gif.gif` |
| ⚠️ Behoben | ~10× HTTP 404 für `/favicon.ico`, `/apple-touch-icon.png` |
| ⚠️ Harmlos | 1× Login fehlgeschlagen (falsches Passwort) |

**Ursache der 404-Fehler:**
- KI-Antworten in der DB enthielten HTML mit `<img src="leon-ai-profile.jpg">` – Datei existiert nicht
- Safari/Browser fragen automatisch `/favicon.ico` und Apple-Touch-Icons an

### Hinzugefügt
- `STRUKTUR.md` → Abschnitt **„Log-Datei auswerten“** (Anleitung, Level-Tabelle, Workflow)
- `routes/pages.py` → Routen für `/favicon.ico`, `/apple-touch-icon.png`
- `static/js/chat.js` → `sanitizeRelativeImages()` blockiert relative Bildpfade aus KI-Antworten

### Geändert
- `utils/errors.py` – harmlose 404-Pfade werden nicht mehr als WARNING geloggt
- `routes/middleware.py` – Terminal-Fehleranzeige für harmlose 404 unterdrückt
- `START_HIER.txt` – Verweis auf `leon.log` und Auswertungs-Anleitung

### Hinweise
- Log bei Problemen: `tail -f data/logs/leon.log`
- Nach jedem Fix Eintrag in `UPDATES.md` schreiben

---

## [2026-06-04] – Modulare Architektur (v4 Refactoring)

**Typ:** Refactoring

### Hinzugefügt

**Backend-Struktur:**
- `config.py` – Zentrale Konfiguration (aus `app.py` ausgelagert)
- `models/database.py` – SQLite-Schema, `init_db()`, `get_db()`
- `services/backup_service.py` – DB-Backup-Logik
- `services/chat_service.py` – Kontext-Aufbau, Token-Schätzung
- `services/memory_service.py` – Automatische Erinnerungen
- `services/ollama_service.py` – Ollama-API-Anbindung
- `services/export_service.py` – Chat-Export (TXT/MD/HTML/JSON)
- `routes/auth.py` – Login/Logout-Routen
- `routes/pages.py` – HTML-Seiten, PWA
- `routes/api.py` – REST-API-Endpunkte
- `routes/chat.py` – SSE-Streaming-Endpunkte
- `routes/middleware.py` – Security-Headers, Request-Logging
- `routes/__init__.py` – Blueprint-Registrierung
- `utils/logging.py` – Strukturiertes Logging → `data/logs/leon.log`
- `utils/security.py` – Auth, Rate-Limit, Origin-Check
- `utils/text.py` – Input-Sanitization
- `utils/errors.py` – Zentraler Fehler-Handler

**Frontend-Struktur:**
- `static/js/api.js` – State + API-Wrapper
- `static/js/ui.js` – Theme, Modals, Sidebar, Einstellungen
- `static/js/artifacts.js` – Live-Vorschau-Panel
- `static/js/chat.js` – Chat, Streaming, Init

**Dokumentation:**
- `STRUKTUR.md` – Projektbriefing & Architektur-Übersicht
- `UPDATES.md` – Dieses Änderungsprotokoll
- `data/logs/` – Log-Verzeichnis (automatisch angelegt)

### Geändert
- `app.py` – Von ~1560 Zeilen auf schlanken Einstiegspunkt reduziert (`create_app()`)
- `templates/index.html` – Inline-JavaScript (~680 Zeilen) durch externe JS-Dateien ersetzt
- Logging: Fehler landen jetzt in `data/logs/leon.log` statt nur in der Konsole
- Terminal-Aktivitäts-Log wird zusätzlich in die Log-Datei geschrieben

### Entfernt
- Monolithischer Code aus `app.py` (auf Module verteilt, Funktionalität bleibt gleich)
- Inline-`<script>`-Block aus `templates/index.html`

### Hinweise
- **Keine Breaking Changes:** Alle URLs, API-Endpunkte und Features funktionieren wie vorher
- Start weiterhin über `Starten.command` oder `python app.py`
- Bei Problemen: `data/logs/leon.log` prüfen
- Übersicht der Architektur: siehe `STRUKTUR.md`

---

## [2026-05-31] – LEON AI v4 (vor Refactoring)

**Typ:** Hinzugefügt / Geändert

### Hinzugefügt
- Passwort-Authentifizierung (ENV-konfigurierbar)
- Rate Limiting (30 Anfragen / 60 s pro IP)
- Kamera / Vision API (`/api/vision`, `/api/vision/stream`)
- PWA Support (`manifest.json`, Service Worker)
- Vision-Modelle in der Modellliste
- Dynamisches Kontext-Fenster (Token-Budget)
- Verbesserte Token-Schätzung (Deutsch-bewusst)
- SQL Injection Fix (parametrisierte Queries)
- Live-Vorschau-Panel für HTML/CSS/JS-Artifacts
- Sidebar einklappbar, Dark Mode, Profil-Avatare

### Geändert
- `debug=False` für Produktion
- Service Worker entfernt aggressives Caching (altes Design-Problem behoben)
- Dynamische IP-Erkennung beim Start

### Hinweise
- Alles in einer einzigen `app.py` (~1560 Zeilen)
- JavaScript vollständig inline in `index.html`

---

<!-- Nächster Eintrag hier einfügen -->
