$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

if (-not $env:PORT) { $env:PORT = "5001" }
if (-not $env:HOST) { $env:HOST = "127.0.0.1" }
if (-not $env:LEON_TERMINAL_ACTIVITY) { $env:LEON_TERMINAL_ACTIVITY = "1" }
if (-not $env:LEON_TERMINAL_LOG_LEVEL) { $env:LEON_TERMINAL_LOG_LEVEL = "CRITICAL" }
if (-not $env:LEON_STARTUP_VERBOSE) { $env:LEON_STARTUP_VERBOSE = "1" }

Write-Host ""
Write-Host "LEON AI is starting..." -ForegroundColor Cyan

if (-not (Test-Path "app.py")) {
  Write-Host "app.py was not found. Please run Starten.ps1 from the LeonAI folder." -ForegroundColor Red
  exit 1
}

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example. You can edit it later." -ForegroundColor Yellow
}

$Python = Join-Path "venv" "Scripts\python.exe"
if (-not (Test-Path $Python)) {
  Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
  $Launcher = Get-Command py -ErrorAction SilentlyContinue
  if ($Launcher) {
    py -m venv venv
  } else {
    python -m venv venv
  }
}

Write-Host "Installing/checking Python packages..." -ForegroundColor Cyan
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt

if (Test-Path "scripts\leon_doctor.py") {
  Write-Host "Running release doctor..." -ForegroundColor Cyan
  & $Python scripts\leon_doctor.py
}

Write-Host ""
Write-Host "LEON AI is ready." -ForegroundColor Green
Write-Host "Open: http://127.0.0.1:$env:PORT" -ForegroundColor Cyan
Write-Host ""

& $Python app.py
