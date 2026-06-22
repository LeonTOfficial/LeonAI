# Erste Schritte mit LEON AI

Diese Anleitung ist der kürzeste Weg vom frischen Download bis zu einem laufenden lokalen LEON-AI-Arbeitsbereich.

Englische Hauptversion: [`../../GETTING_STARTED.md`](../../GETTING_STARTED.md)

## 1. Was du brauchst

| Voraussetzung | Empfehlung |
| --- | --- |
| Python | 3.11 oder 3.12 |
| Git | Aktuelle stabile Version |
| Ollama | Lokal installiert und gestartet |
| Browser | Safari, Chrome, Edge oder Firefox |
| Speicherplatz | ca. 6,5 bis 7,5 GB mit den empfohlenen Modellen |

## 2. Ollama-Modelle installieren

```bash
ollama pull llama3
ollama pull llama3.2:1b
```

`llama3` ist das Standardmodell für Chats. `llama3.2:1b` wird für schnelle Auto-Titel genutzt.

## 3. LEON AI herunterladen

```bash
git clone https://github.com/LeonTOfficial/LeonAI.git
cd LeonAI
```

## 4. Lokale Einstellungen erstellen

```bash
cp .env.example .env
```

Öffne `.env` und passe Passwort, Secret Key, Port und Modell bei Bedarf an. Lade `.env` niemals auf GitHub hoch.

## 5. App starten

### macOS

```bash
chmod +x Starten.command
./Starten.command
```

### Windows PowerShell

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\Starten.ps1
```

### Linux / normales macOS-Terminal

```bash
chmod +x start.sh
./start.sh
```

## 6. LEON AI öffnen

```text
http://127.0.0.1:5001
```

Beim ersten Start öffnet LEON AI einen Setup-Screen, in dem du Vorname und Passwort festlegst.

## 7. Erste Dinge zum Testen

- Stelle eine normale Frage auf Deutsch.
- Bitte um eine kleine HTML-Seite und öffne die Artifacts-Vorschau.
- Bitte um ein Mermaid-Flussdiagramm.
- Bitte um ein Balkendiagramm mit Beispieldaten.
- Öffne das Dashboard und nutze **Diagnose kopieren**, wenn etwas komisch wirkt.

Wenn etwas nicht funktioniert, lies [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).
