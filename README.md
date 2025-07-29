# BringVoiceAssistant - Sprachgesteuerter Einkaufslisten-Assistent

Ein intelligenter Sprachassistent, der auf das Wakeword "Alexa" hört, deine gesprochenen Einkaufswünsche versteht und automatisch zur Bring! Einkaufsliste hinzufügt.

## 🎯 Features
- **Wakeword-Erkennung**: Aktivierung durch "Alexa" (Picovoice Porcupine)
- **Spracherkennung**: Aufnahme und Transkription deiner Einkaufsliste
- **KI-Analyse**: Extraktion von Einkaufsartikeln mit Google Gemini 2.5 Flash
- **Bring! Integration**: Automatisches Hinzufügen zur Bring! Einkaufsliste
- **Audio-Feedback**: Sprachbestätigung der hinzugefügten Artikel
- **Dauerbetrieb**: Kontinuierliches Lauschen auf Wakeword

## 🚀 Setup

### 1. Repository klonen
```bash
git clone <repository-url>
cd BringVoiceAssistant
```

### 2. Virtuelle Umgebung einrichten
```bash
cd voice-assistant
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. Umgebungsvariablen konfigurieren
Erstelle eine `.env`-Datei im `voice-assistant` Verzeichnis:
```env
# Google Gemini API
GEMINI_API_KEY=dein_gemini_api_key

# Bring! API Credentials
BRING_EMAIL=deine_bring_email
BRING_PASSWORD=dein_bring_passwort
BRING_LIST_NAME=Zuhause  # Name deiner Bring! Liste

# Picovoice Access Key
PICOVOICE_ACCESS_KEY=dein_picovoice_key
```

## 🎮 Nutzung

### Starten
```bash
python main.py
```

### Bedienung
1. **Warten**: Das System lauscht kontinuierlich auf "Alexa"
2. **Aktivieren**: Sage "Alexa" und warte auf das Bestätigungssignal
3. **Sprechen**: Nach dem Signal deine Einkaufsliste aufsagen (z.B. "Ich brauche Milch, Brot und Äpfel")
4. **Bestätigung**: Das System analysiert die Sprache und fügt Artikel zur Bring! Liste hinzu
5. **Feedback**: Audio-Bestätigung der hinzugefügten Artikel

### Beispiel-Session
```
Einkaufslisten-Sprachassistent gestartet!
Warte auf Wakeword...
[Wakeword-Modul] Wakeword erkannt!
Bitte sprich deine Einkaufsliste nach dem Signal.

Erkannte Artikel:
- Milch
- Brot  
- Äpfel

Verbinde mit Bring! API...
Füge Artikel zur Liste 'Zuhause' hinzu...
- 'Milch' hinzugefügt.
- 'Brot' hinzugefügt.
- 'Äpfel' hinzugefügt.

Alle Artikel erfolgreich zu Bring! hinzugefügt.
```

## 🔧 Technische Details

### Dependencies
- `bring-api`: Bring! API Integration (via pip)
- `google-generativeai`: Gemini 2.5 Flash für Textanalyse
- `picovoice`: Wakeword-Erkennung
- `sounddevice`: Audio-Aufnahme
- `aiohttp`: Asynchrone HTTP-Requests
- `python-dotenv`: Umgebungsvariablen-Management

### Architektur
```
src/
├── wakeword.py    # Picovoice Wakeword-Erkennung
├── gemini.py      # Gemini API Integration
├── tts.py         # Text-to-Speech Feedback
└── bring_api.py   # Bring! API Wrapper
```

## 🏠 Deployment auf Raspberry Pi

### Hardware-Anforderungen
- Raspberry Pi 3B+ oder neuer
- USB-Mikrofon oder HAT mit Mikrofon
- Lautsprecher oder Kopfhörer

### Installation
```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python und Audio-Dependencies
sudo apt install python3-pip python3-venv portaudio19-dev -y

# Projekt setup (wie oben)
git clone <repository-url>
cd BringVoiceAssistant/voice-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Autostart (systemd)
```bash
# Service-Datei erstellen
sudo nano /etc/systemd/system/voice-assistant.service
```

```ini
[Unit]
Description=Voice Assistant Bring
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/BringVoiceAssistant/voice-assistant
Environment=PATH=/home/pi/BringVoiceAssistant/voice-assistant/venv/bin
ExecStart=/home/pi/BringVoiceAssistant/voice-assistant/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Service aktivieren
sudo systemctl enable voice-assistant.service
sudo systemctl start voice-assistant.service
```

## 🔑 API-Keys erhalten

### Google Gemini API
1. Besuche [Google AI Studio](https://aistudio.google.com/)
2. Erstelle einen kostenlosen API-Key
3. Füge ihn als `GEMINI_API_KEY` in die `.env` ein

### Picovoice Access Key
1. Registriere dich bei [Picovoice Console](https://console.picovoice.ai/)
2. Erstelle einen kostenlosen Access Key
3. Füge ihn als `PICOVOICE_ACCESS_KEY` in die `.env` ein

### Bring! Credentials
- Verwende deine normalen Bring! App Login-Daten
- `BRING_LIST_NAME` muss exakt dem Namen deiner Liste in der App entsprechen

## 🛠️ Troubleshooting

### Audio-Probleme
```bash
# Verfügbare Audio-Geräte anzeigen
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Bring! API Fehler
- Überprüfe Email/Passwort in `.env`
- Stelle sicher, dass der Listenname exakt übereinstimmt
- Teste die Bring! App auf dem Handy

### Wakeword-Erkennung
- Mikrofon-Berechtigung prüfen
- Spreche "Alexa" deutlich und nicht zu leise
- Teste verschiedene Mikrofon-Positionen 