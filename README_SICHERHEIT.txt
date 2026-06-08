LEON AI - Sicherheit, Datenschutz und Release-Hinweise

Stand: Juni 2026

Kurzfassung
LEON AI ist als lokale Mac-App gebaut. Standardmaessig lauscht der Server nur auf 127.0.0.1, nutzt Login/First-Setup, schuetzt schreibende Requests mit CSRF-Tokens und speichert private Laufzeitdaten ausserhalb des GitHub-Repositories.

Wichtig: Dieses Projekt ist lokal-first, aber nicht als oeffentlicher Internet-Service gedacht. Wenn HOST=0.0.0.0 genutzt wird, muss das Netzwerk bewusst vertraut sein.

1. Sicherheitsziel

LEON AI soll fuer persoenliche lokale Nutzung sicher und nachvollziehbar sein:

- Private Chats bleiben lokal in SQLite.
- Die App ist standardmaessig nur auf dem eigenen Mac erreichbar.
- Schreibende Browser-Anfragen brauchen einen gueltigen CSRF-Token.
- Fremde Webseiten duerfen keine Cross-Site-Schreibaktionen ausloesen.
- Fehler zeigen im Browser eine Request-ID, aber keine internen Stacktraces.
- Logs enthalten technische Details fuer Debugging, gehoeren aber nicht auf GitHub.

2. Beweise im Code

| Schutz | Datei | Was dort passiert |
| --- | --- | --- |
| Lokaler Host und Defaults | config.py | PORT, HOST, Auth, Rate Limit, Ollama-Modelle und Pfade werden zentral gesetzt. |
| Login und First Setup | routes/auth.py | Login, Logout, einmalige Ersteinrichtung mit Passwort und Vorname. |
| Passwort-Hashing und CSRF | utils/security.py | Passwortpruefung, CSRF-Token, Login-Decorator, Rate-Limit-Helfer und Origin-Check. |
| Security Header | routes/middleware.py | CSP, X-Frame-Options, Referrer-Policy, Permissions-Policy, Request-ID und Origin-Gate. |
| Fehlerabschirmung | utils/errors.py | Unerwartete Fehler werden geloggt, im Browser aber nur mit sauberer Meldung und Request-ID gezeigt. |
| Strukturierte Logs | utils/logging.py | Rotierende Logdatei data/logs/leon.log, Request-ID pro Anfrage, Terminal standardmaessig ruhig. |
| Datenbank-Schema | models/database.py | SQLite-Tabellen, Migrationen, Branching-Felder, Artifact-Versionen. |
| Backups | services/backup_service.py | SQLite-Backups mit Manifest/Integritaetsinformationen. |
| Privacy-Werkzeuge | utils/privacy.py | Zaehlen und geschuetztes Loeschen lokaler Datenbereiche. |
| Health Checks | utils/system_health.py | Pruefung von Datenbank, Logs, Backups und Ollama. |
| Sichere Chat-Ausgabe | static/js/chat.js | Markdown-Rendering, Farbtags, DOMPurify-Integration und CSRF bei Frontend-Requests. |
| Sandbox-Vorschau | static/js/artifacts.js | Artifact-Vorschau im iframe, relative Asset-Pfade werden neutralisiert, Terminal/Fehler-Bridge fuer Preview. |
| Private Dateien aus Git ausschliessen | .gitignore | .env, data/, backup/, venv/, Datenbanken, Logs und lokale HTML-Snapshots werden ausgeschlossen. |

3. Was getestet wurde

Die Test-Suite wird so gestartet:

./venv/bin/python -m unittest discover -s tests -q

Aktueller Umfang:

- Login und geschuetzte Seiten.
- First-Setup-Flow.
- CSRF-Pflicht fuer POST/PATCH/DELETE.
- Origin-Block fuer fremde Schreibzugriffe.
- Fehlerantworten ohne interne Details, aber mit Request-ID.
- Chat-Raeume, Nachrichten, Branching und aktiver Ast.
- Auto-Titel mit llama3.2:1b.
- Artifact-Versionen, Dedupe, Speichern, Loeschen und ZIP-Export.
- Artifact-Preview-Vertraege fuer HTML/CSS/JS, Tailwind, Pyodide, Terminal und Fehlerliste.
- Mermaid/Chart.js/Farbtags als Frontend-Vertraege.
- Dashboard-, Privacy-, Health- und Backup-Funktionen.
- .gitignore-/README-/Dokumentationsvertraege.

Die Tests liegen hier:

- tests/test_core.py
- tests/test_ui_flows.py

4. Warum das fuer lokale Nutzung sicher ist

LEON AI reduziert die wichtigsten Risiken fuer eine lokale KI-App:

- Keine Cloud-Pflicht: Chats und App-Daten liegen lokal in data/.
- Keine offene Netzwerkfreigabe: HOST ist standardmaessig 127.0.0.1.
- Kein Klartext-Passwort im Terminal: Das Startskript zeigt das Passwort nicht an.
- Kein ungeschuetztes Schreiben: CSRF-Token und Origin-Check schuetzen kritische Browser-Requests.
- Keine internen Fehlerdetails im Browser: Nutzer sehen eine Request-ID, Entwickler finden Details in leon.log.
- Keine privaten Laufzeitdaten im Repository: .gitignore blockiert lokale Daten, Backups, Logs und Secrets.
- Vorschaubereich isoliert: KI-generiertes HTML laeuft in einem iframe; relative Bild-/Assetpfade werden neutralisiert.

5. Was bewusst nicht versprochen wird

- LEON AI ist kein gehaerteter Multi-User-Cloud-Service.
- Die lokale Ollama-Installation und installierte Modelle muessen separat gepflegt werden.
- Wenn HOST=0.0.0.0 gesetzt wird, ist der Server im Netzwerk erreichbar. Das sollte nur bewusst und in vertrauten Netzwerken passieren.
- KI-generierter Code kann fachlich falsch oder unsicher sein. Die Artifact-Vorschau ist zum Testen gedacht, nicht als Sicherheitsfreigabe.

6. Was nicht auf GitHub gehoert

Niemals veroeffentlichen:

- .env
- data/
- backup/
- venv/
- *.db
- *.log
- lokale HTML-Snapshots wie "LEON AI.html"
- alte Entwurfsdateien wie README_FEINSCHLIFF.txt
- GitHub Tokens, Passwoerter oder private API-Keys

Wenn ein GitHub Token versehentlich geteilt wurde, sofort bei GitHub widerrufen und neu erstellen.

7. Start auf macOS

Normal:

chmod +x Starten.command
./Starten.command

Falls macOS die Datei aus Sicherheitsgruenden nicht direkt ausfuehrt:

cd "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Leon-ai"
chmod +x Starten.command
./Starten.command

8. Debugging und Logs

Die Terminal-Ausgabe ist bewusst minimal. Details stehen hier:

data/logs/leon.log

Nuetzliche Befehle:

tail -n 80 data/logs/leon.log
grep -E "ERROR|WARNING" data/logs/leon.log

Jede wichtige Anfrage bekommt eine Request-ID. Wenn im Browser ein Fehler mit ID angezeigt wird, kann diese ID im Log gesucht werden.

9. Lizenzhinweis

LEON AI ist proprietaere Source-Available-Software. Die offizielle App/Demo darf normal genutzt werden. Der Quellcode darf zu Lern-, Pruefungs- und Evaluierungszwecken angesehen werden. Kopieren, Veraendern, Weitergeben, eigenes Hosting oder kommerzielle Nutzung des Quellcodes erfordern vorherige schriftliche Genehmigung von Leon.
