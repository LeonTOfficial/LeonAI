#!/bin/bash
cd "$(dirname "$0")"

# LEON AI Startskript - Port 5001, weil macOS oft Port 5000 belegt.
export PORT="${PORT:-5001}"
export HOST="${HOST:-127.0.0.1}"

GRN='\033[92m'; YLW='\033[93m'; RED='\033[91m'; CYN='\033[96m'; RST='\033[0m'; BLD='\033[1m'
clear

echo -e "${CYN}${BLD}⚡ LEON AI wird gestartet...${RST}"

if curl -fsS "http://127.0.0.1:$PORT/login" >/dev/null 2>&1 || curl -fsS "http://127.0.0.1:$PORT/" >/dev/null 2>&1; then
  echo -e "${GRN}✅ LEON AI läuft bereits auf Port $PORT.${RST}"
  echo -e "🌐 Öffne: ${CYN}http://127.0.0.1:$PORT${RST}"
  open "http://127.0.0.1:$PORT" >/dev/null 2>&1 || true
  echo -e "\nDu kannst dieses Fenster schließen oder offen lassen."
  read -n 1 -s -r -p "Taste drücken zum Schließen..."
  exit 0
fi

if [ ! -f "app.py" ]; then
  echo -e "${RED}❌ app.py nicht gefunden. Starten.command muss direkt im Leon-ai Ordner liegen.${RST}"
  read -n 1 -s -r -p "Taste drücken zum Schließen..."
  exit 1
fi

if [ ! -d "templates" ]; then
  if [ -d "template" ]; then
    echo -e "${YLW}⚠️  Ordner heißt template. Erstelle kompatiblen templates-Ordner...${RST}"
    mkdir -p templates
    cp -f template/index.html templates/index.html 2>/dev/null || true
    cp -f template/dashboard.html templates/dashboard.html 2>/dev/null || true
  else
    echo -e "${RED}❌ templates Ordner fehlt.${RST}"
    read -n 1 -s -r -p "Taste drücken zum Schließen..."
    exit 1
  fi
fi

if [ -x "venv/bin/python" ]; then
  PYTHON="venv/bin/python"
elif [ -x "Venv/bin/python" ]; then
  PYTHON="Venv/bin/python"
else
  echo -e "${YLW}🐍 venv fehlt. Erstelle neue virtuelle Umgebung...${RST}"
  python3 -m venv venv || {
    echo -e "${RED}❌ Konnte venv nicht erstellen. Prüfe, ob Python 3 installiert ist.${RST}"
    read -n 1 -s -r -p "Taste drücken zum Schließen..."
    exit 1
  }
  PYTHON="venv/bin/python"
fi

echo -e "${CYN}📦 Installiere/prüfe Pakete...${RST}"
"$PYTHON" -m pip install -q --upgrade pip
"$PYTHON" -m pip install -q -r requirements.txt || {
  echo -e "${RED}❌ Konnte requirements.txt nicht installieren.${RST}"
  echo "Tipp: Internet prüfen."
  read -n 1 -s -r -p "Taste drücken zum Schließen..."
  exit 1
}

if command -v ollama >/dev/null 2>&1; then
  if ! curl -s "http://localhost:11434/api/tags" > /dev/null 2>&1; then
    echo -e "${YLW}⚙️  Starte Ollama im Hintergrund...${RST}"
    ollama serve > /dev/null 2>&1 &
    sleep 3
  fi
else
  echo -e "${YLW}⚠️  Ollama wurde nicht gefunden. Chat funktioniert erst, wenn Ollama installiert/läuft.${RST}"
fi

LOCAL_IP=$("$PYTHON" -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2>/dev/null || echo "127.0.0.1")

echo -e "\n${GRN}✅ SYSTEM BEREIT${RST}"
echo -e "-------------------------------------------"
echo -e "🖥️  MAC SAFARI: ${CYN}http://localhost:$PORT${RST}"
echo -e "🔒 Netzwerk:   nur lokal erreichbar. Für Handy bewusst starten mit: HOST=0.0.0.0 ./Starten.command"
echo -e "-------------------------------------------"
echo -e "🔑 Login-Passwort wird aus .env oder dem Standardwert gelesen."
echo -e "   Tipp: In .env LEON_PASSWORD ändern. Das Passwort wird hier nicht ausgegeben."
echo -e "-------------------------------------------\n"

"$PYTHON" app.py
