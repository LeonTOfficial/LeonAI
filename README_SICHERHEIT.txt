LEON AI - Sicherheit & Hinweise

Geprüft/gefixt:
- App läuft lokal auf Port 5001.
- Host ist standardmäßig 127.0.0.1, also nur auf deinem Mac erreichbar.
- Login ist aktiv, Standardpasswort ist leon2026.
- Passwort wird beim Start nicht im Terminal angezeigt.
- Session-Cookies sind HttpOnly und SameSite=Lax.
- Security-Header sind gesetzt.
- Fremde Cross-Site-POSTs werden blockiert.
- SQL-Abfragen sind parametrisiert.
- Chat-Markdown wird im Frontend mit DOMPurify bereinigt.
- Codeblöcke haben Kopieren- und Datei-Export-Buttons.
- data/ und backup/ werden nicht gelöscht.
- Altes Service-Worker-Caching wird entfernt, damit kein altes Design hängen bleibt.

Empfohlen:
Lege später eine .env Datei neben app.py an:

LEON_PASSWORD=dein-neues-passwort
SECRET_KEY=ein-langer-zufallswert

Hinweis:
Die App ist für lokale Nutzung auf deinem Mac gedacht.
