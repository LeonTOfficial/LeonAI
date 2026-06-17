# LEON AI Fehlerhilfe

Diese Anleitung hilft bei den häufigsten Setup- und Laufzeitproblemen. Sie ist bewusst praktisch aufgebaut: Symptom finden, wahrscheinliche Ursache prüfen und zuerst die sichere Lösung ausprobieren.

Englische Hauptversion: [`../../TROUBLESHOOTING.md`](../../TROUBLESHOOTING.md)

## Schneller Gesundheitscheck

Führe den Release Doctor im Projektordner aus:

```bash
python scripts/leon_doctor.py
```

Für eine tiefere Prüfung mit Python-Tests:

```bash
python scripts/leon_doctor.py --run-tests
```

Wenn die App startet, aber etwas komisch wirkt, prüfe zusätzlich das lokale Log:

```text
data/logs/leon.log
```

Das Log ist lokale Laufzeitinformation. Es sollte nicht öffentlich hochgeladen werden, wenn private Prompts, Pfade oder Diagnosedetails darin stehen.

## Häufige Probleme

| Symptom | Wahrscheinliche Ursache | Was du versuchen kannst |
| --- | --- | --- |
| Browser öffnet `http://127.0.0.1:5001` nicht | Der Flask-Server läuft nicht oder der Port ist belegt | Starter neu ausführen und Terminalausgabe prüfen. Wenn Port `5001` belegt ist, `PORT` in `.env` ändern. |
| Ollama wird als offline angezeigt | Ollama läuft nicht oder das Modell fehlt | Ollama starten, dann `ollama pull llama3` und `ollama pull llama3.2:1b` ausführen. |
| Login akzeptiert das Passwort nicht | Das Passwort in `.env` ist anders oder First Setup hat bereits ein lokales Passwort gesetzt | Lokale `.env` prüfen. Nicht committen. |
| Windows blockiert den Starter | PowerShell blockiert lokale Skripte für diese Sitzung | Erst `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, dann `.\Starten.ps1` ausführen. |
| Python-Versionsfehler | Python ist zu alt | Python 3.10 oder neuer nutzen. Python 3.11/3.12 werden empfohlen und in CI getestet. |
| Installation der Abhängigkeiten schlägt fehl | `pip` ist alt, die virtuelle Umgebung ist beschädigt oder das Netzwerk hatte einen Fehler | Virtuelle Umgebung aktivieren, `python -m pip install --upgrade pip` ausführen und danach `requirements.txt` erneut installieren. |
| Artifacts-Vorschau bleibt leer | Generierter Code ist unvollständig, Browser-Bibliotheken laden nicht oder das iframe braucht einen Refresh | Fehler-Tab öffnen, Aktualisieren klicken und zuerst ein kleines HTML-Beispiel testen. |
| Mermaid-Diagramm rendert nicht | Mermaid-Syntax ist ungültig | Ein einfacheres `flowchart TD` verlangen und fehlerhafte Pfeile wie `|label|>` vermeiden. |
| Chart.js-Ausgabe bleibt Code | Die Antwort nutzt nicht die erwartete Chart-Block-Struktur | Nach einem umzäunten `chart`-Codeblock mit gültigem JSON fragen. |
| Pyodide/Python lädt nicht | CDN/Netzwerk lädt nicht oder der Browser blockiert das Skript | Vorschau neu laden, Fehler-Tab prüfen und mit Internetzugang erneut versuchen. |
| GitHub Actions schlagen fehl, obwohl die App lokal läuft | CI findet Doku-, Test- oder Browser-Fixture-Probleme, die lokal nicht immer auffallen | Fehlenden Job öffnen, ersten roten Schritt prüfen und den passenden Befehl lokal ausführen. |

## Logs und Request IDs

LEON AI versucht, im Browser klare und sichere Fehlermeldungen zu zeigen. Tiefere Diagnosedetails bleiben lokal in den Logs.

| Ort | Wofür es gedacht ist |
| --- | --- |
| Browser-Fehlermeldung | Kurze, sichere Erklärung für den Nutzer. |
| Request ID | Verbindet eine Browser-Meldung mit einem Backend-Logeintrag. |
| `data/logs/leon.log` | Lokale Diagnosehistorie für Start, Anfragen, Warnungen und kontrollierte Fehler. |
| Debug-/Health-Bereiche im Dashboard | Schneller Überblick über Zustand, Warnungen, Backups und aktuelle App-Aktivität. |

Wenn du einen Bug meldest, nenne die sichtbare Fehlermeldung und die Request ID, falls eine angezeigt wird. Poste keine privaten Prompts, `.env`-Werte, API-Schlüssel, lokalen Pfade oder vollständigen Logs öffentlich.

## Sichere Bugreport-Checkliste

Vor einem Issue hilft meistens diese kurze Prüfung:

- Prüfe, ob du auf dem aktuellen `main`-Branch oder dem neuesten Release-Tag bist.
- Führe `python scripts/leon_doctor.py` aus.
- Notiere Betriebssystem, Python-Version, Browser und Ollama-Modell.
- Beschreibe, was du direkt vor dem Fehler geklickt oder eingegeben hast.
- Füge Screenshots nur hinzu, wenn keine privaten Daten sichtbar sind.

Sicherheitsrelevante Funde bitte nach [`SECURITY.md`](SECURITY.md) behandeln und nicht als öffentlichen Bugreport mit Exploit-Details posten.
