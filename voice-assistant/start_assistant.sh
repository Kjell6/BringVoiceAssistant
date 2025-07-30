#!/bin/bash

# Wrapper-Skript für den Voice Assistant
# Stellt die richtige Umgebung für systemd bereit

# Arbeitsverzeichnis setzen
cd /home/kjell/BringVoiceAssistant/voice-assistant

# Virtuelle Umgebung aktivieren
source venv/bin/activate

# Vollständigen PATH setzen
export PATH="/home/kjell/BringVoiceAssistant/voice-assistant/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Audio-Umgebung setzen
export PULSE_RUNTIME_PATH=/run/user/1000/pulse
export XDG_RUNTIME_DIR=/run/user/1000

# Python-Pfad setzen
export PYTHONPATH=/home/kjell/BringVoiceAssistant/voice-assistant

# Programm starten
exec python main.py 