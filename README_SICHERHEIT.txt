LEON AI - Sicherheit und GitHub-Hinweise

Kurz gesagt:
LEON AI ist standardmaessig fuer die lokale Nutzung auf deinem Mac gebaut. Die App bindet sich an 127.0.0.1, nutzt ein Login, schuetzt schreibende Anfragen mit CSRF-Tokens und speichert private Laufzeitdaten nicht im GitHub-Repository.

Wichtige Sicherheitsfunktionen:
- Lokaler Betrieb: HOST=127.0.0.1 bedeutet, dass die App nur auf deinem Mac erreichbar ist.
- Login: Bei frischen Installationen wird das Passwort im First-Setup festgelegt.
- Migration: LEON_PASSWORD in .env bleibt als Fallback fuer bestehende Installationen.
- Session-Schutz: Cookies sind HttpOnly und SameSite=Lax.
- CSRF-Schutz: POST/PUT/PATCH/DELETE brauchen einen gueltigen Sicherheits-Token.
- Origin-Schutz: Fremde Cross-Site-Schreibzugriffe werden blockiert.
- Security Header: Content-Security-Policy, X-Frame-Options, Referrer-Policy und Permissions-Policy sind gesetzt.
- Datenbank: SQLite-Abfragen sind parametrisiert.
- Chat-Inhalte: Markdown wird im Frontend mit DOMPurify bereinigt.
- Vorschau: Artifact-HTML laeuft in einem Sandbox-iframe und wird ueber blob:-URLs geladen.
- Relative KI-Bildpfade werden neutralisiert, damit keine ungewollten lokalen 404-Requests entstehen.
- Logs und Fehler enthalten Request-IDs, damit Probleme nachvollziehbar bleiben.

Was NICHT auf GitHub gehoert:
- .env
- data/
- backup/
- venv/
- *.db
- *.log
- lokale HTML-Snapshots wie "LEON AI.html"
- alte lokale Entwurfsdateien wie README_FEINSCHLIFF.txt

Die .gitignore ist genau dafuer vorbereitet.

GitHub-Token / Passwoerter:
Wenn ein Token oder Passwort versehentlich irgendwo gepostet wurde, sofort widerrufen und neu erstellen. GitHub Personal Access Tokens beginnen oft mit "ghp_". So ein Token ist wie ein Passwort.

Start auf macOS:
Normal:

chmod +x Starten.command
./Starten.command

Falls macOS die Datei aus Sicherheitsgruenden nicht direkt ausfuehrt:

cd "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Leon-ai"
chmod +x Starten.command
./Starten.command

Lizenzhinweis:
LEON AI ist proprietaere Source-Available-Software. Die offizielle App/Demo darf normal genutzt werden. Der Quellcode darf zu Lern-, Pruefungs- und Evaluierungszwecken angesehen werden. Kopieren, Veraendern, Weitergeben, eigenes Hosting oder kommerzielle Nutzung des Quellcodes erfordern vorherige schriftliche Genehmigung von Leon.
