# LEON AI Troubleshooting

This guide is for the most common setup and runtime problems. It is intentionally practical: find the symptom, check the likely cause, then try the safest fix first.

German version: [`docs/de/TROUBLESHOOTING.md`](docs/de/TROUBLESHOOTING.md)

## Quick Health Check

Run the release doctor from the project folder:

```bash
python scripts/leon_doctor.py
```

For a deeper check, include the Python test suite:

```bash
python scripts/leon_doctor.py --run-tests
```

If the app starts but something behaves strangely, also check the local log:

```text
data/logs/leon.log
```

The log is local runtime data. It should not be uploaded publicly if it contains private prompts, paths, or diagnostic details.

## Common Problems

| Symptom | Likely cause | What to try |
| --- | --- | --- |
| Browser cannot open `http://127.0.0.1:5001` | The Flask server is not running or another process owns the port | Restart the launcher and check the terminal output. If port `5001` is busy, change `PORT` in `.env`. |
| Ollama shows as offline | Ollama is not running or the model is missing | Start Ollama, then run `ollama pull llama3` and `ollama pull llama3.2:1b`. |
| Login does not accept the password | `.env` password differs from what you typed, or first setup already created a local password | Check your local `.env`. Do not commit it. |
| Windows blocks the launcher | PowerShell execution policy blocks local scripts for this session | Start with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then run `.\Starten.ps1`. |
| Python version errors | Python is too old | Use Python 3.10 or newer. Python 3.11/3.12 are recommended and used in CI. |
| Dependency installation fails | `pip` is old, the virtual environment is broken, or the network failed | Activate the virtual environment, run `python -m pip install --upgrade pip`, then install `requirements.txt` again. |
| Artifacts preview is blank | Generated code is incomplete, browser libraries failed to load, or the iframe needs a refresh | Open the Error tab, click Refresh, and try a small HTML example first. |
| You are unsure whether preview itself is broken | The generated artifact may be broken rather than LEON AI's preview | Click **Self-test** in the Artifacts panel. If the self-test renders, the preview engine is basically working. |
| Mermaid diagram does not render | Mermaid syntax is invalid | Ask for a simpler `flowchart TD` diagram and avoid malformed arrows such as `|label|>`. |
| Chart.js output stays as code | The answer is not using the expected chart block shape | Ask for a fenced `chart` code block with valid JSON. |
| Pyodide/Python does not load | CDN/network loading failed or the browser blocked the script | Reload the preview, check the Error tab, and try again with internet access. |
| GitHub Actions fail but local app works | CI catches docs, tests, or browser fixture issues that do not always show locally | Open the failing job, check the first red step, then run the matching command locally. |

## Logs And Request IDs

LEON AI tries to show clean user-facing errors while keeping deeper diagnostic details in local logs.

| Place | What it is for |
| --- | --- |
| Browser error message | Short, safe explanation for the user. |
| Request ID | Helps connect a browser error to a backend log entry. |
| `data/logs/leon.log` | Local diagnostic history for startup, requests, warnings, and controlled errors. |
| Dashboard debug/health areas | Quick overview of health, warnings, backups, and recent app activity. |

When reporting a bug, include the visible error message and the request ID if one is shown. Avoid posting private prompts, `.env` values, API keys, local paths, or full logs publicly.

## Safe Bug Report Checklist

Before opening an issue, this small checklist usually helps:

- Confirm you are on the latest `main` branch or the latest release tag.
- Run `python scripts/leon_doctor.py`.
- Note your operating system, Python version, browser, and Ollama model.
- Describe what you clicked or typed before the problem happened.
- Include screenshots only if they do not show private data.

Security-sensitive findings should follow [`SECURITY.md`](SECURITY.md), not a public bug report.
