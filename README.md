> 🇩🇪 **German version available:** Scroll down for the German description of this project.

# LEON AI

![Local-First Architecture](https://img.shields.io/badge/local--first-architecture-5357ff?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-ready-111827?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.x-17a673?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-private-d99b18?style=for-the-badge)
![License](https://img.shields.io/badge/license-source--available%20proprietary-red?style=for-the-badge)

![LEON AI Chat Demo](docs/screenshots/leon-ai-chat-demo.png)

## What Is LEON AI?

LEON AI is a private, local AI workspace for your own computer. It brings chat, code, live previews, diagrams, Python experiments, memory, logs, and dashboards into one clean place. It is built for people who want AI power on macOS, Windows, or Linux without giving every thought and project file to a cloud service.

## Features That Make You Want To Try It

- **Local AI models:** Run with Ollama and use models such as `llama3`, `llama3.2:1b`, LLaVA, and more.
- **Smart chat workspace:** Auto titles, pinned chats, branching, favorites, memory, export, and German-first answers.
- **Colored text in chat:** Ask LEON AI to mark nouns red, highlight key ideas, or color-code feedback with safe color tags.
- **Native diagrams and charts:** Mermaid diagrams and Chart.js graphs render directly inside the chat instead of staying as raw code.
- **Super Artifacts:** Generate HTML, CSS, JavaScript, Tailwind layouts, and Python snippets with a live preview panel.
- **Browser Python sandbox:** Python can run inside the browser through Pyodide, isolated from your operating system.
- **Vision image uploads:** Upload images and ask LEON AI to describe, analyze, or reason about them when a vision model is installed.
- **Privacy dashboard:** See activity, token usage, health checks, backups, logs, and privacy tools in one dashboard.
- **First setup:** On a fresh install, choose your own password and first name before using the app.

![LEON AI Artifacts Preview](docs/screenshots/leon-ai-artifacts-preview.png)

![LEON AI Dashboard](docs/screenshots/leon-ai-dashboard.png)

## Quick Start / Installation

LEON AI is a cross-platform Flask application. macOS includes a convenience launcher, while Windows laptops/desktops and Linux systems run the same project through Python and Ollama.

1. Install [Ollama](https://ollama.com/) and pull the recommended models:

```bash
ollama pull llama3
ollama pull llama3.2:1b
```

2. Clone the project and enter the folder:

```bash
git clone https://github.com/LeonTOfficial/LeonAI.git
cd LeonAI
```

3. Create your local settings file:

```bash
cp .env.example .env
```

4. Open `.env` and adjust the basics:

```env
LEON_PASSWORD=change-this-before-sharing
SECRET_KEY=use-a-long-random-secret
PORT=5001
HOST=127.0.0.1
OLLAMA_MODEL=llama3
```

5. Start LEON AI on your platform:

### macOS

```bash
chmod +x Starten.command
./Starten.command
```

If macOS refuses to run the command file for security reasons, open Terminal and run:

```bash
cd "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Leon-ai"
chmod +x Starten.command
./Starten.command
```

### Windows PowerShell

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell blocks the virtual environment activation script, run PowerShell as your user and allow scripts for the current session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Linux

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

6. Open the app in your browser:

```text
http://127.0.0.1:5001
```

On a fresh install, LEON AI shows a first-setup screen where you choose your own password and first name. After that, the normal login is used.

![LEON AI Login Light and Dark Mode](docs/screenshots/leon-ai-login-light-dark.png)

## Storage Needed

| Component | Approx. size |
| --- | ---: |
| LEON AI code + Python dependencies | about 0.5 - 1.5 GB |
| Llama 3 model | about 4.7 GB |
| Llama 3.2 1B model | about 1.3 GB |
| Total recommended space | about 6.5 - 7.5 GB |

## For The Nerds

Want to know how the security model works, how the SQLite schema is structured, or how the v4 modular architecture is organized?

Read:

- [`STRUKTUR.md`](STRUKTUR.md) for the architecture, modules, routes, services, and frontend structure.
- [`SECURITY.md`](SECURITY.md) for the local security model, `.env` guidance, dependency notes, and vulnerability reporting.
- [`TESTING.md`](TESTING.md) for the current unit-test and QA workflow.

## Verified Engineering Highlights

LEON AI is not just a visual demo. The project includes a focused test suite and a documented security model.

- **Tested backend flows:** login, setup, room creation, branching, artifact history, backups, privacy actions, and error handling.
- **Tested frontend contracts:** CSRF headers, colored chat tags, Mermaid/Chart.js integration markers, Pyodide wiring, and artifact preview controls.
- **Security evidence:** CSRF protection lives in `utils/security.py`, request/security headers in `routes/middleware.py`, error shielding in `utils/errors.py`, and the `.gitignore` excludes local secrets, databases, backups, logs, and virtual environments.
- **Current QA command:** `./venv/bin/python -m unittest discover -s tests -q`

Real folder overview:

```text
LeonAI/
├── app.py
├── config.py
├── Starten.command
├── README.md
├── SECURITY.md
├── STRUKTUR.md
├── TESTING.md
├── LICENSE
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
├── tests/
│   ├── test_core.py
│   └── test_ui_flows.py
└── docs/
    └── screenshots/
```

## About The Developer

I am **Leon**, 17 years old, born in 2009, from Germany, and preparing for a future in business informatics. LEON AI is my personal learning project for understanding how modern full-stack software is planned, built, tested, secured, refactored, and led from zero to release.

This project was built with **AI-Assisted Development**. That matters: it shows how a young developer can use AI as a serious engineering partner to build modular, secure, and usable software faster while still learning the important decisions behind every layer.

A special highlight: I received the **Landespreis Medienbildung** for creating educational content that makes AI easier to understand: what machine learning is at a high level, what is behind systems like ChatGPT, and why it matters outside the tech bubble.

## License & Support
**LEON AI is proprietary source-available software.** All rights are reserved by the author: **Copyright © 2026 Leon**.

| Use case | Permission required? | Notes |
| --- | --- | --- |
| Use the official app/demo privately | **No** | Anyone may use the official app/demo normally and free of charge for private use. |
| Read the source code for learning or review | **No** | The repository may be viewed for educational, evaluation, and review purposes. |
| Copy, modify, self-host, redistribute, rebrand, or publish the source code | **Yes** | Prior written permission from Leon is required. |
| Commercial use or integration into another product/service | **Yes** | A separate written permission/license is required. |

LEON AI is designed as a portable local AI workspace for macOS, Windows laptops/desktops, and Linux systems when Python, the required dependencies, and Ollama are available on that machine.

Community feedback is very welcome: please test the app actively, try real workflows, and open a GitHub Issue whenever you find a bug, have a question, or want to suggest an improvement. For security-sensitive reports, use the private reporting process described in [`SECURITY.md`](SECURITY.md).

If you like this project, leave a **star ⭐️** and **follow** me on GitHub. It supports my learning path and helps me keep building better, safer, and more useful AI projects.

---

# LEON AI

![Lokale Priorität](https://img.shields.io/badge/Lokale%20Priorit%C3%A4t-5357ff?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-bereit-111827?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.x-17a673?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-privat-d99b18?style=for-the-badge)
![License](https://img.shields.io/badge/license-source--available%20proprietary-red?style=for-the-badge)

![LEON AI Chat Demo](docs/screenshots/leon-ai-chat-demo.png)

## Was Ist LEON AI?

LEON AI ist dein privater, lokaler KI-Arbeitsplatz für deinen eigenen Computer. Die App verbindet Chat, Code, Live-Vorschau, Diagramme, Python-Tests, Speicher, Logs und Dashboard in einer Oberfläche. Sie ist für Menschen gebaut, die KI unter macOS, Windows oder Linux stark nutzen wollen, ohne jedes Projekt und jeden Gedanken an einen Cloud-Dienst zu schicken.

## Features, Die Hunger Machen

- **Lokale KI-Modelle:** Läuft mit Ollama und Modellen wie `llama3`, `llama3.2:1b`, LLaVA und mehr.
- **Starker Chat-Arbeitsbereich:** Auto-Titel, angepinnte Chats, Branching, Favoriten, Speicher, Export und konsequent deutsche Antworten.
- **Farbe im Chat:** Lass LEON AI Nomen rot markieren, Schlüsselstellen hervorheben oder Feedback farbig strukturieren.
- **Diagramme und Charts im Chat:** Mermaid-Diagramme und Chart.js-Grafiken werden direkt gerendert statt nur als Code angezeigt.
- **Super-Artifacts:** HTML, CSS, JavaScript, Tailwind-Oberflächen und Python-Snippets direkt in einer Live-Vorschau ausprobieren.
- **Python-Sandbox im Browser:** Python läuft über Pyodide im Browser und nicht direkt auf deinem Betriebssystem.
- **Vision-Bild-Uploads:** Bilder hochladen und analysieren lassen, wenn ein Vision-Modell installiert ist.
- **Privacy Dashboard:** Aktivität, Token-Nutzung, Health Checks, Backups, Logs und Datenschutz-Werkzeuge an einem Ort.
- **First Setup:** Bei einer frischen Installation legst du dein eigenes Passwort und deinen Vornamen fest.

![LEON AI Artifacts Preview](docs/screenshots/leon-ai-artifacts-preview.png)

![LEON AI Dashboard](docs/screenshots/leon-ai-dashboard.png)

## Quick Start / Installation

LEON AI ist eine plattformübergreifende Flask-Anwendung. macOS enthält einen Komfort-Starter, während Windows-Laptops/-Desktops und Linux-Systeme dasselbe Projekt über Python und Ollama starten.

1. Installiere [Ollama](https://ollama.com/) und lade die empfohlenen Modelle:

```bash
ollama pull llama3
ollama pull llama3.2:1b
```

2. Klone das Projekt und öffne den Ordner:

```bash
git clone https://github.com/LeonTOfficial/LeonAI.git
cd LeonAI
```

3. Erstelle deine lokale Konfiguration:

```bash
cp .env.example .env
```

4. Öffne `.env` und passe die wichtigsten Werte an:

```env
LEON_PASSWORD=neues-langes-passwort
SECRET_KEY=langer-geheimer-wert
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

Wenn macOS die Datei aus Sicherheitsgründen nicht direkt ausführen kann, öffne das Terminal und gib ein:

```bash
cd "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Leon-ai"
chmod +x Starten.command
./Starten.command
```

### Windows PowerShell

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Wenn PowerShell das Aktivieren der virtuellen Umgebung blockiert, erlaube Skripte nur für die aktuelle Sitzung:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Linux

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

Bei einer frischen Installation erscheint zuerst ein Setup-Screen. Dort legst du dein eigenes Passwort und deinen Vornamen fest. Danach erscheint nur noch der normale Login.

![LEON AI Login Light and Dark Mode](docs/screenshots/leon-ai-login-light-dark.png)

## Speicherbedarf

| Komponente | Ungefährer Speicherbedarf |
| --- | ---: |
| LEON AI Code + Python-Abhängigkeiten | ca. 0,5 - 1,5 GB |
| Llama 3 Modell | ca. 4,7 GB |
| Llama 3.2 1B Modell | ca. 1,3 GB |
| Gesamtbedarf | ca. 6,5 - 7,5 GB |

## Für Die Nerds

Du willst wissen, wie sicher das ist oder wie die modulare Architektur aus dem v4-Refactoring funktioniert?

Lies:

- [`STRUKTUR.md`](STRUKTUR.md) für Architektur, Module, Routen, Services und Frontend-Struktur.
- [`SECURITY.md`](SECURITY.md) für das lokale Sicherheitsmodell, `.env`-Hinweise, Abhängigkeiten und das Melden von Sicherheitslücken.
- [`TESTING.md`](TESTING.md) für Unit Tests, QA und Prüfschritte.

## Geprüfte Technik-Highlights

LEON AI ist nicht nur eine schöne Oberfläche. Das Projekt hat eine gezielte Test-Suite und ein dokumentiertes Sicherheitsmodell.

- **Getestete Backend-Flows:** Login, First Setup, Chat-Erstellung, Branching, Artifact-Versionen, Backups, Privacy-Aktionen und Fehlerbehandlung.
- **Getestete Frontend-Verträge:** CSRF-Header, Farbtags im Chat, Mermaid/Chart.js-Marker, Pyodide-Anbindung und Artifact-Vorschau-Controls.
- **Sicherheitsbelege:** CSRF-Schutz liegt in `utils/security.py`, Security-Header in `routes/middleware.py`, Fehlerabschirmung in `utils/errors.py`, und die `.gitignore` schließt lokale Secrets, Datenbanken, Backups, Logs und virtuelle Umgebungen aus.
- **Aktueller QA-Befehl:** `./venv/bin/python -m unittest discover -s tests -q`

Echte Ordnerstruktur:

```text
LeonAI/
├── app.py
├── config.py
├── Starten.command
├── README.md
├── SECURITY.md
├── STRUKTUR.md
├── TESTING.md
├── LICENSE
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
├── tests/
│   ├── test_core.py
│   └── test_ui_flows.py
└── docs/
    └── screenshots/
```

## Über Den Entwickler

Ich bin **Leon**, 17 Jahre alt, Jahrgang 2009, aus Deutschland und bereite mich auf meinen Weg in die Wirtschaftsinformatik/Angewandteinformatik vor. LEON AI ist mein persönliches Lernprojekt, um zu verstehen, wie moderne Full-Stack-Software geplant, gebaut, getestet, abgesichert, refaktoriert und von null bis zum Release geführt wird.

Das Projekt ist mit **AI-Assisted Development** entstanden. Genau das ist ein wichtiger Punkt: Es zeigt, wie effizient man heute als junger Entwickler mit KI als ernstem Engineering-Partner modulare, sichere und brauchbare Software bauen kann.

Ein besonderes Highlight: Ich habe den **Landespreis Medienbildung** für ein KI-Projekt erhalten, mit dem ich Bildungsinhalte erstellt habe, die KI verständlicher machen: was Machine Learning grob bedeutet, was hinter Systemen wie ChatGPT steckt und warum das Thema auch außerhalb der Tech-Welt wichtig ist.

## Lizenz & Support
**LEON AI ist proprietäre Source-Available-Software.** Alle Rechte bleiben beim Urheber: **Copyright © 2026 Leon**.

| Nutzung | Genehmigung nötig? | Erklärung |
| --- | --- | --- |
| Offizielle App/Demo privat nutzen | **Nein** | Jeder darf die offizielle App/Demo völlig normal und kostenlos für den privaten Gebrauch nutzen. |
| Quellcode zu Lern- oder Prüfzwecken ansehen | **Nein** | Das Repository darf zu Bildungs-, Evaluierungs- und Review-Zwecken gelesen werden. |
| Quellcode kopieren, verändern, selbst hosten, weiterverbreiten, umbenennen oder veröffentlichen | **Ja** | Dafür ist vorher eine schriftliche Genehmigung von Leon erforderlich. |
| Kommerzielle Nutzung oder Integration in ein anderes Produkt/einen Dienst | **Ja** | Dafür ist eine gesonderte schriftliche Genehmigung/Lizenz erforderlich. |

LEON AI ist als portabler lokaler KI-Arbeitsplatz für macOS, Windows-Laptops/-Desktops und Linux-Systeme konzipiert, wenn Python, die benötigten Abhängigkeiten und Ollama auf dem Gerät verfügbar sind.

Community-Feedback ist ausdrücklich willkommen: Teste die App gerne aktiv, probiere echte Workflows aus und eröffne jederzeit ein GitHub Issue, wenn ein Fehler auftritt, eine Frage offen ist oder du eine Verbesserung vorschlagen möchtest. Für sicherheitskritische Meldungen nutze bitte den privaten Meldeweg aus [`SECURITY.md`](SECURITY.md).

Wenn dir das Projekt gefällt, lass gerne einen **Stern ⭐️** da und **folge** mir auf GitHub. Damit unterstützt du meinen Lernweg und hilfst mir, weitere bessere, sicherere und nützlichere KI-Projekte zu bauen.
