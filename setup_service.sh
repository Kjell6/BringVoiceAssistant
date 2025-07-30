#!/bin/bash

# Setup-Skript für den Bring Voice Assistant Service
echo "🚀 Setup für Bring Voice Assistant Service..."

# Prüfe ob wir als root laufen
if [ "$EUID" -ne 0 ]; then
    echo "❌ Bitte führe dieses Skript mit sudo aus:"
    echo "sudo bash setup_service.sh"
    exit 1
fi

# Aktueller Benutzer ermitteln
ACTUAL_USER=$(logname)
if [ -z "$ACTUAL_USER" ]; then
    ACTUAL_USER=$(who am i | awk '{print $1}')
fi

echo "👤 Benutzer: $ACTUAL_USER"

# Service-Datei kopieren
echo "📁 Kopiere Service-Datei..."
cp voice-assistant.service /etc/systemd/system/

# Benutzer in Service-Datei anpassen
sed -i "s/User=pi/User=$ACTUAL_USER/g" /etc/systemd/system/voice-assistant.service
sed -i "s/Group=pi/Group=$ACTUAL_USER/g" /etc/systemd/system/voice-assistant.service

# Arbeitsverzeichnis anpassen
CURRENT_DIR=$(pwd)
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$CURRENT_DIR/voice-assistant|g" /etc/systemd/system/voice-assistant.service
sed -i "s|Environment=PATH=.*|Environment=PATH=$CURRENT_DIR/voice-assistant/venv/bin|g" /etc/systemd/system/voice-assistant.service
sed -i "s|Environment=PYTHONPATH=.*|Environment=PYTHONPATH=$CURRENT_DIR/voice-assistant|g" /etc/systemd/system/voice-assistant.service
sed -i "s|ExecStart=.*|ExecStart=$CURRENT_DIR/voice-assistant/venv/bin/python main.py|g" /etc/systemd/system/voice-assistant.service

# Benutzer zur audio-Gruppe hinzufügen
echo "🔊 Füge Benutzer zur audio-Gruppe hinzu..."
usermod -a -G audio $ACTUAL_USER

# Service aktivieren
echo "⚙️  Aktiviere Service..."
systemctl daemon-reload
systemctl enable voice-assistant.service

echo "✅ Setup abgeschlossen!"
echo ""
echo "📋 Nächste Schritte:"
echo "1. Starte den Service: sudo systemctl start voice-assistant.service"
echo "2. Prüfe den Status: sudo systemctl status voice-assistant.service"
echo "3. Zeige Logs an: sudo journalctl -u voice-assistant.service -f"
echo ""
echo "🛑 Service stoppen: sudo systemctl stop voice-assistant.service"
echo "🔄 Service neustarten: sudo systemctl restart voice-assistant.service" 