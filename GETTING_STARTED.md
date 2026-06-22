# Getting Started With LEON AI

This guide is the shortest path from a fresh clone to a running local LEON AI workspace.

German version: [`docs/de/GETTING_STARTED.md`](docs/de/GETTING_STARTED.md)

## 1. What You Need

| Requirement | Recommended |
| --- | --- |
| Python | 3.11 or 3.12 |
| Git | Latest stable version |
| Ollama | Installed and running locally |
| Browser | Safari, Chrome, Edge, or Firefox |
| Disk space | About 6.5 - 7.5 GB with the recommended models |

## 2. Install Ollama Models

```bash
ollama pull llama3
ollama pull llama3.2:1b
```

`llama3` is the default chat model. `llama3.2:1b` is used for fast auto-title generation.

## 3. Download LEON AI

```bash
git clone https://github.com/LeonTOfficial/LeonAI.git
cd LeonAI
```

## 4. Create Local Settings

```bash
cp .env.example .env
```

Open `.env` and adjust the password, secret key, port, and model if needed. Never upload `.env` to GitHub.

## 5. Start The App

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

### Linux / macOS Terminal

```bash
chmod +x start.sh
./start.sh
```

## 6. Open LEON AI

```text
http://127.0.0.1:5001
```

On first launch, LEON AI opens a setup screen where you choose your first name and password.

## 7. First Things To Try

- Ask a normal German question.
- Ask for a small HTML page and open the Artifacts preview.
- Ask for a Mermaid flowchart.
- Ask for a bar chart with example data.
- Open the dashboard and use **Diagnose kopieren** if something feels wrong.

If something does not work, read [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).
