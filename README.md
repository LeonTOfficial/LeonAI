# LEON AI

![Local First](https://img.shields.io/badge/local-first-5357ff?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-ready-111827?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.x-17a673?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-private-d99b18?style=for-the-badge)
![License](https://img.shields.io/badge/license-source--available%20proprietary-red?style=for-the-badge)

[PLATZHALTER: Big image/GIF of the chat in action]

## What Is LEON AI?

LEON AI is a private, local AI workspace for your Mac. It brings chat, code, live previews, diagrams, Python experiments, memory, logs, and dashboards into one clean place. It is built for people who want AI power without giving every thought and project file to a cloud service.

## Features That Make You Want To Try It

- **Local AI models:** Run with Ollama and use models such as `llama3`, `llama3.2:1b`, LLaVA, and more.
- **Smart chat workspace:** Auto titles, pinned chats, branching, favorites, memory, export, and German-first answers.
- **Colored text in chat:** Ask LEON AI to mark nouns red, highlight key ideas, or color-code feedback with safe color tags.
- **Native diagrams and charts:** Mermaid diagrams and Chart.js graphs render directly inside the chat instead of staying as raw code.
- **Super Artifacts:** Generate HTML, CSS, JavaScript, Tailwind layouts, and Python snippets with a live preview panel.
- **Browser Python sandbox:** Python can run inside the browser through Pyodide, isolated from your Mac system.
- **Vision image uploads:** Upload images and ask LEON AI to describe, analyze, or reason about them when a vision model is installed.
- **Privacy dashboard:** See activity, token usage, health checks, backups, logs, and privacy tools in one dashboard.
- **First setup:** On a fresh install, choose your own password and first name before using the app.

[PLATZHALTER: Screenshot - Split view: code on the left, rendered live preview with Mermaid/Charts in the Artifacts panel on the right]

[PLATZHALTER: Screenshot - Dashboard with token statistics and Privacy Center]

## Quick Start / Installation

1. Install [Ollama](https://ollama.com/) and pull the recommended models:

```bash
ollama pull llama3
ollama pull llama3.2:1b
```

2. Clone the project and enter the folder:

```bash
git clone <your-repository-url>
cd Leon-ai
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

5. Start LEON AI on macOS:

```bash
chmod +x Starten.command
./Starten.command
```

6. Open the app:

```text
http://127.0.0.1:5001
```

On a fresh install, LEON AI shows a first-setup screen where you choose your own password and first name. After that, the normal login is used.

## For The Nerds

Want to know how the security model works, how the SQLite schema is structured, or how the v4 modular architecture is organized?

Read:

- [`STRUKTUR.md`](STRUKTUR.md) for the architecture, modules, routes, services, and frontend structure.
- [`README_SICHERHEIT.txt`](README_SICHERHEIT.txt) for the local security model, `.env` guidance, and release safety notes.
- [`TESTING.md`](TESTING.md) for the current unit-test and QA workflow.

## About The Developer

I am **Leon**, 17 years old, born in 2009, from Germany, and preparing for a future in business informatics. LEON AI is my personal learning project for understanding how modern full-stack software is planned, built, tested, secured, refactored, and led from zero to release.

This project was built with **AI-Assisted Development**. That matters: it shows how a young developer can use AI as a serious engineering partner to build modular, secure, and usable software faster while still learning the important decisions behind every layer.

A special highlight: I received the **Landespreis Medienbildung** for creating educational content that makes AI easier to understand: what machine learning is at a high level, what is behind systems like ChatGPT, and why it matters outside the tech bubble.

## License & Support
**LEON AI is proprietary software**. All rights reserved by the author **(Copyright ©️ 2026 Leon)**. You may view the source code strictly for educational and review purposes, but any copying, distribution, modification, or commercial use requires prior written permission.

If you like this project, leave a **star ⭐️** and **follow** me on GitHub. It supports my learning path and helps me keep building better, safer, and more useful AI projects.

---

# LEON AI

![Lokal Zuerst](https://img.shields.io/badge/lokal-zuerst-5357ff?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-bereit-111827?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.x-17a673?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-privat-d99b18?style=for-the-badge)
![License](https://img.shields.io/badge/license-source--available%20proprietary-red?style=for-the-badge)

[PLATZHALTER: Großes Bild/GIF vom Chat in Aktion]

## Was Ist LEON AI?

LEON AI ist dein privater, lokaler KI-Arbeitsplatz für den Mac. Die App verbindet Chat, Code, Live-Vorschau, Diagramme, Python-Tests, Speicher, Logs und Dashboard in einer Oberfläche. Sie ist für Menschen gebaut, die KI stark nutzen wollen, ohne jedes Projekt und jeden Gedanken an einen Cloud-Dienst zu schicken.

## Features, Die Hunger Machen

- **Lokale KI-Modelle:** Läuft mit Ollama und Modellen wie `llama3`, `llama3.2:1b`, LLaVA und mehr.
- **Starker Chat-Arbeitsbereich:** Auto-Titel, angepinnte Chats, Branching, Favoriten, Speicher, Export und konsequent deutsche Antworten.
- **Farbe im Chat:** Lass LEON AI Nomen rot markieren, Schlüsselstellen hervorheben oder Feedback farbig strukturieren.
- **Diagramme und Charts im Chat:** Mermaid-Diagramme und Chart.js-Grafiken werden direkt gerendert statt nur als Code angezeigt.
- **Super-Artifacts:** HTML, CSS, JavaScript, Tailwind-Oberflächen und Python-Snippets direkt in einer Live-Vorschau ausprobieren.
- **Python-Sandbox im Browser:** Python läuft über Pyodide im Browser und nicht direkt auf deinem Mac-System.
- **Vision-Bild-Uploads:** Bilder hochladen und analysieren lassen, wenn ein Vision-Modell installiert ist.
- **Privacy Dashboard:** Aktivität, Token-Nutzung, Health Checks, Backups, Logs und Datenschutz-Werkzeuge an einem Ort.
- **First Setup:** Bei einer frischen Installation legst du dein eigenes Passwort und deinen Vornamen fest.

[PLATZHALTER: Screenshot - Geteilte Ansicht: Code links, gerenderte Live-Vorschau (Mermaid/Charts) im Artifacts-Panel rechts]

[PLATZHALTER: Screenshot - Das Dashboard mit Token-Statistiken und Privacy Center]

## Quick Start / Installation

1. Installiere [Ollama](https://ollama.com/) und lade die empfohlenen Modelle:

```bash
ollama pull llama3
ollama pull llama3.2:1b
```

2. Klone das Projekt und öffne den Ordner:

```bash
git clone <deine-repository-url>
cd Leon-ai
```

3. Erstelle deine lokale Konfiguration:

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

5. Starte LEON AI auf macOS:

```bash
chmod +x Starten.command
./Starten.command
```

6. Öffne die App:

```text
http://127.0.0.1:5001
```

Bei einer frischen Installation erscheint zuerst ein Setup-Screen. Dort legst du dein eigenes Passwort und deinen Vornamen fest. Danach erscheint nur noch der normale Login.

## Für Die Nerds

Du willst wissen, wie sicher das ist oder wie die modulare Architektur aus dem v4-Refactoring funktioniert?

Lies:

- [`STRUKTUR.md`](STRUKTUR.md) für Architektur, Module, Routen, Services und Frontend-Struktur.
- [`README_SICHERHEIT.txt`](README_SICHERHEIT.txt) für das lokale Sicherheitsmodell, `.env`-Hinweise und Release-Sicherheit.
- [`TESTING.md`](TESTING.md) für Unit Tests, QA und Prüfschritte.

## Über Den Entwickler

Ich bin **Leon**, 17 Jahre alt, Jahrgang 2009, aus Deutschland und bereite mich auf meinen Weg in die Wirtschaftsinformatik/Angewandteinformatik vor. LEON AI ist mein persönliches Lernprojekt, um zu verstehen, wie moderne Full-Stack-Software geplant, gebaut, getestet, abgesichert, refaktoriert und von null bis zum Release geführt wird.

Das Projekt ist mit **AI-Assisted Development** entstanden. Genau das ist ein wichtiger Punkt: Es zeigt, wie effizient man heute als junger Entwickler mit KI als ernstem Engineering-Partner modulare, sichere und brauchbare Software bauen kann.

Ein besonderes Highlight: Ich habe den **Landespreis Medienbildung** für ein KI-Projekt erhalten, mit dem ich Bildungsinhalte erstellt habe, die KI verständlicher machen: was Machine Learning grob bedeutet, was hinter Systemen wie ChatGPT steckt und warum das Thema auch außerhalb der Tech-Welt wichtig ist.

## Lizenz & Support
**LEON AI ist proprietäre Software**. Alle Rechte vorbehalten **(Copyright ©️ 2026 Leon)**. Der Quellcode darf zu Lern- und Prüfungszwecken eingesehen werden. Jedes Kopieren, Verändern, Weitergeben oder die kommerzielle Nutzung erfordert jedoch eine vorherige schriftliche Genehmigung des Urhebers.

Wenn dir das Projekt gefällt, lass gerne einen **Stern ⭐️** da und **folge** mir auf GitHub. Damit unterstützt du meinen Lernweg und hilfst mir, weitere bessere, sicherere und nützlichere KI-Projekte zu bauen.
