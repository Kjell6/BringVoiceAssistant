#!/bin/bash

# Verwaltungsskript für den Bring Voice Assistant Service

SERVICE_NAME="voice-assistant.service"

case "$1" in
    start)
        echo "🚀 Starte Voice Assistant Service..."
        sudo systemctl start $SERVICE_NAME
        ;;
    stop)
        echo "🛑 Stoppe Voice Assistant Service..."
        sudo systemctl stop $SERVICE_NAME
        ;;
    restart)
        echo "🔄 Starte Voice Assistant Service neu..."
        sudo systemctl restart $SERVICE_NAME
        ;;
    status)
        echo "📊 Status des Voice Assistant Service:"
        sudo systemctl status $SERVICE_NAME
        ;;
    logs)
        echo "📝 Logs des Voice Assistant Service (Strg+C zum Beenden):"
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    enable)
        echo "✅ Aktiviere Voice Assistant Service für Autostart..."
        sudo systemctl enable $SERVICE_NAME
        ;;
    disable)
        echo "❌ Deaktiviere Voice Assistant Service für Autostart..."
        sudo systemctl disable $SERVICE_NAME
        ;;
    *)
        echo "🎮 Voice Assistant Service Verwaltung"
        echo ""
        echo "Verwendung: $0 {start|stop|restart|status|logs|enable|disable}"
        echo ""
        echo "Befehle:"
        echo "  start   - Service starten"
        echo "  stop    - Service stoppen"
        echo "  restart - Service neustarten"
        echo "  status  - Service-Status anzeigen"
        echo "  logs    - Live-Logs anzeigen"
        echo "  enable  - Autostart aktivieren"
        echo "  disable - Autostart deaktivieren"
        echo ""
        echo "Beispiele:"
        echo "  $0 start    # Service starten"
        echo "  $0 status   # Status prüfen"
        echo "  $0 logs     # Logs anzeigen"
        ;;
esac 