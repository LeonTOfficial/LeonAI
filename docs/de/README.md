# LEON AI

![Local-First Architektur](https://img.shields.io/badge/Local--First-Architektur-5357ff?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-bereit-111827?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.x-17a673?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-privat-d99b18?style=for-the-badge)
![Lizenz](https://img.shields.io/badge/Lizenz-source--available%20proprietary-red?style=for-the-badge)

> Dies ist die deutsche Dokumentation zu **LEON AI**.  
> Die englische Hauptdokumentation findest du im Repository-Root: [`README.md`](../../README.md).

![LEON AI Chat Demo](../screenshots/leon-ai-chat-demo.png)

**Chat-Arbeitsbereich:** LEON AI verbindet lokale KI-Chats, Code-Ausgaben, gerenderte Artefakte und Projektkontext in einer Oberfläche.

## Was ist LEON AI?

LEON AI ist ein privater, lokaler KI-Arbeitsbereich für deinen eigenen Computer. Die App bringt Chat, Code, Live-Vorschau, Diagramme, Python-Experimente, Memory, Logs und Dashboards an einen sauberen Ort. Sie ist für macOS, Windows und Linux gedacht und legt den Fokus auf Privatsphäre, Sicherheit und starke deutschsprachige Nutzung.

## Features, die Lust aufs Ausprobieren machen

- **Lokale KI-Modelle:** Läuft mit Ollama und Modellen wie `llama3`, `llama3.2:1b`, LLaVA und mehr.
- **Smarter Chat-Arbeitsbereich:** Auto-Titel, angepinnte Chats, Branching, Favoriten, Memory, Export und deutschfreundliche Antworten.
- **Farben im Chat:** Lass LEON AI Nomen rot markieren, Schlüsselstellen hervorheben oder Feedback farbig strukturieren.
- **Native Diagramme und Charts:** Mermaid-Diagramme und Chart.js-Grafiken werden direkt im Chat gerendert.
- **Super Artifacts:** HTML, CSS, JavaScript, Tailwind-Layouts und Python-Snippets direkt in einer Live-Vorschau prüfen.
- **Python-Sandbox im Browser:** Python läuft über Pyodide im Browser und nicht direkt auf deinem Betriebssystem.
- **Vision-Bild-Uploads:** Bilder hochladen und mit passenden Vision-Modellen beschreiben, analysieren oder erklären lassen.
- **Privacy Dashboard:** Aktivität, Token-Nutzung, Health Checks, Backups, Restore, Logs und Datenschutz-Werkzeuge an einem Ort.
- **First Setup:** Bei einer frischen Installation legst du dein eigenes Passwort und deinen Vornamen fest.

![LEON AI Artifacts Preview](../screenshots/leon-ai-artifacts-preview.png)

**Artifacts-Vorschau:** Generiertes HTML, CSS, JavaScript und Tailwind-artige Layouts können direkt neben dem Chat geprüft werden.

## Download / Klonen und Installieren

LEON AI ist eine plattformübergreifende Flask-App. Jede Plattform hat einen empfohlenen Startweg, damit Anfänger nicht lange suchen müssen.

1. Installiere [Ollama](https://ollama.com/) und lade die empfohlenen Modelle:

```bash
ollama pull llama3
ollama pull llama3.2:1b
```

2. Lade das Hauptprojekt mit Git herunter und öffne den Ordner:

```bash
git clone https://github.com/LeonTOfficial/LeonAI.git
cd LeonAI
```

3. Erstelle deine lokale Einstellungsdatei:

```bash
cp .env.example .env
```

4. Öffne `.env` und passe die wichtigsten Werte an:

```env
LEON_PASSWORD=aendere-das-vor-dem-teilen
SECRET_KEY=nutze-einen-langen-zufaelligen-wert
PORT=5001
HOST=127.0.0.1
OLLAMA_MODEL=llama3
```

5. Starte LEON AI auf deiner Plattform:

### macOS

```bash
chmod +x Starten.command
./Starten.command
```

Wenn macOS die Datei aus Sicherheitsgründen nicht direkt starten möchte, öffne das Terminal im Projektordner und führe dieselben Befehle dort aus:

```bash
chmod +x Starten.command
./Starten.command
```

### Windows PowerShell

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\Starten.ps1
```

Der PowerShell-Starter erstellt die virtuelle Umgebung, installiert Abhängigkeiten, legt `.env` aus `.env.example` an, führt den Release Doctor aus und startet die App.

### Linux / normales macOS-Terminal

```bash
chmod +x start.sh
./start.sh
```

Der Shell-Starter nutzt dieselben Projektdateien wie macOS und Windows, funktioniert aber aus einem normalen Terminal heraus.

### Manueller Python-Fallback

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

6. Öffne die App im Browser:

```text
http://127.0.0.1:5001
```

Bei einer frischen Installation zeigt LEON AI zuerst einen Setup-Screen. Dort legst du dein eigenes Passwort und deinen Vornamen fest. Danach wird der normale Login verwendet.

Vor Veröffentlichungen kannst du im Hauptprojekt den Release Doctor ausführen:

```bash
python scripts/leon_doctor.py
```

Für eine ausführlichere lokale Prüfung:

```bash
python scripts/leon_doctor.py --run-tests
```

![LEON AI Login Light and Dark Mode](../screenshots/leon-ai-login-light-dark.png)

**Login und First Setup:** Beim ersten Start fragt LEON AI nach Vorname und Passwort, bevor der lokale Arbeitsbereich geöffnet wird.

## Speicherbedarf

| Komponente | Ungefährer Speicherbedarf |
| --- | ---: |
| LEON AI Code + Python-Abhängigkeiten | ca. 0,5 bis 1,5 GB |
| Llama 3 Modell | ca. 4,7 GB |
| Llama 3.2 1B Modell | ca. 1,3 GB |
| Empfohlener Gesamtbedarf | ca. 6,5 bis 7,5 GB |

## Für die Nerds

Du willst wissen, wie das Sicherheitsmodell funktioniert, wie das SQLite-Schema aufgebaut ist oder wie die modulare Architektur organisiert ist?

Lies:

- [`STRUKTUR.md`](STRUKTUR.md) für Architektur, Module, Routen, Services und Frontend-Struktur.
- [`SECURITY.md`](SECURITY.md) für das lokale Sicherheitsmodell, `.env`-Hinweise, Abhängigkeiten und das Melden von Sicherheitslücken.
- [`TESTING.md`](TESTING.md) für Unit Tests, Browser-QA und den aktuellen QA-Workflow.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) für Feedback-Regeln, Issues und genehmigte Beiträge.
- [`ROADMAP.md`](ROADMAP.md) für erledigte Punkte, nächste Schritte, spätere Ideen und gewünschtes Feedback.
- [`CHANGELOG.md`](CHANGELOG.md) für öffentliche Release Notes und Versionshistorie.

![LEON AI Dashboard](../screenshots/leon-ai-dashboard.png)

**Dashboard-Vorschau:** Datenschutzinformationen, Token-Nutzung, Logs, Systemzustand und Projektaktivität im integrierten Dashboard.

## Geprüfte Technik-Highlights

LEON AI ist nicht nur eine schöne Oberfläche. Das Projekt hat eine gezielte Test-Suite und ein dokumentiertes Sicherheitsmodell.

- **Getestete Backend-Flows:** Login, Setup, Chat-Erstellung, Branching, Artifact-Historie, Backup-Restore, Privacy-Aktionen und Fehlerbehandlung.
- **Getestete Frontend-Verträge:** CSRF-Header, Farbtags im Chat, Mermaid/Chart.js-Marker, Pyodide-Anbindung und Artifact-Vorschau-Controls.
- **CI-Checks:** GitHub Actions im Hauptrepo testen Python 3.11 und 3.12, prüfen JavaScript und führen Browser-QA aus.
- **Browser-QA:** Playwright prüft Login/Setup, Dashboard, Chat-Shell, Farbtags, Charts, Mermaid-Diagramme und Artifact-Vorschau mit festen Browser-Fixtures.
- **Release Doctor:** `scripts/leon_doctor.py` prüft Doku, Pflichtdateien, CI-Verkabelung und versehentlich getrackte Runtime-Daten.
- **Sicherheitsbelege:** CSRF-Schutz liegt in `utils/security.py`, Security Header in `routes/middleware.py`, Fehlerabschirmung in `utils/errors.py`, und `.gitignore` hält lokale Runtime-Daten und Secrets aus Git heraus.
- **Aktueller QA-Befehl:** `./venv/bin/python -m unittest discover -s tests -q`

Echte Ordnerübersicht:

```text
LeonAI/
├── app.py
├── config.py
├── Starten.command
├── Starten.ps1
├── start.sh
├── README.md
├── SECURITY.md
├── STRUKTUR.md
├── TESTING.md
├── CHANGELOG.md
├── ROADMAP.md
├── LICENSE
├── CONTRIBUTING.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       └── test.yml
├── tests/
│   ├── browser/
│   ├── test_core.py
│   └── test_ui_flows.py
├── scripts/
│   └── leon_doctor.py
├── models/
│   └── database.py
├── routes/
│   ├── api.py
│   ├── auth.py
│   ├── chat.py
│   ├── middleware.py
│   └── pages.py
├── services/
│   ├── artifact_service.py
│   ├── backup_service.py
│   ├── chat_service.py
│   ├── memory_service.py
│   ├── ollama_service.py
│   ├── profile_service.py
│   └── room_service.py
├── static/
│   └── js/
│       ├── api.js
│       ├── artifacts.js
│       ├── chat.js
│       └── ui.js
├── templates/
│   ├── dashboard.html
│   └── index.html
└── docs/
    └── screenshots/
```

## Über den Entwickler

Ich bin **Leon**, 16 Jahre alt, Jahrgang 2009, aus Deutschland und bereite mich auf eine Zukunft in der Wirtschaftsinformatik vor. LEON AI ist mein persönliches Lernprojekt, um moderne Full-Stack-Software wirklich zu verstehen: modulare Architektur, sichere Authentifizierung, lokale Daten, Tests und reale Veröffentlichung.

Dieses Projekt ist mit **AI-Assisted Development** entstanden. Genau das ist ein wichtiger Punkt: Es zeigt, wie ein junger Entwickler KI als ernsthaften Engineering-Partner nutzen kann, um modulare, sichere und brauchbare Software schneller zu bauen. Codequalität, Tests und Dokumentation spiegeln diese Zusammenarbeit wider.

Ein besonderes Highlight: Ich habe den **Landespreis Medienbildung** für Bildungsinhalte erhalten, die KI verständlicher machen: was Machine Learning grob bedeutet, was hinter Systemen wie ChatGPT steckt und wie man KI-Werkzeuge verantwortungsvoll nutzt.

## Lizenz & Support

**LEON AI ist proprietäre Source-Available-Software.** Alle Rechte liegen beim Autor: **Copyright © 2026 Leon**.

| Nutzung | Genehmigung nötig? | Hinweis |
| --- | --- | --- |
| Offizielle App/Demo privat nutzen | **Nein** | Jeder darf die offizielle App/Demo normal und kostenlos privat nutzen. |
| Quellcode zum Lernen oder Prüfen ansehen | **Nein** | Das Repository darf zu Lern-, Bewertungs- und Review-Zwecken angesehen werden. |
| Quellcode kopieren, verändern, selbst hosten, weiterverbreiten, rebranden oder veröffentlichen | **Ja** | Dafür ist vorherige schriftliche Genehmigung von Leon nötig. |
| Kommerzielle Nutzung oder Integration in ein anderes Produkt/einen Dienst | **Ja** | Dafür ist eine separate schriftliche Genehmigung/Lizenz nötig. |

LEON AI ist als portabler lokaler KI-Arbeitsbereich für macOS, Windows-Laptops/Desktop-PCs und Linux-Systeme gedacht, wenn Python, die benötigten Abhängigkeiten und Ollama auf dem Gerät verfügbar sind.

Feedback ist sehr willkommen: Bitte teste die App aktiv, probiere echte Workflows aus und öffne im Hauptrepo ein GitHub Issue, wenn du einen Fehler findest, eine Frage hast oder eine Verbesserung vorschlagen möchtest. Für Sicherheitsfunde lies bitte [`SECURITY.md`](SECURITY.md).

Wenn dir das Projekt gefällt, lass im Hauptrepo gerne einen **Stern ⭐️** da und **folge** mir auf GitHub. Das unterstützt meinen Lernweg und hilft mir, bessere, sicherere und nützlichere KI-Projekte zu bauen.
