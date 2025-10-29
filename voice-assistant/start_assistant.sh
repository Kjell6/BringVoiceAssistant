#!/bin/bash

# Wrapper-Skript für den Voice Assistant
# Stellt die richtige Umgebung für systemd bereit

set -euo pipefail

# Arbeitsverzeichnis setzen
cd /home/kjell/BringVoiceAssistant/voice-assistant

# Pfade/Umgebung
export PULSE_RUNTIME_PATH=/run/user/1000/pulse
export XDG_RUNTIME_DIR=/run/user/1000
export PYTHONPATH=/home/kjell/BringVoiceAssistant/voice-assistant

PYTHON_BIN="/home/kjell/BringVoiceAssistant/voice-assistant/venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python nicht gefunden: $PYTHON_BIN"
  exit 1
fi

# Programm starten (unbuffered Output für Journal)
exec "$PYTHON_BIN" -u main.py