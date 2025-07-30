# BringVoiceAssistant - Sprachgesteuerter Einkaufslisten-Assistent

Ein intelligenter Sprachassistent, der auf das Wakeword "Alexa" hört, deine gesprochenen Einkaufswünsche versteht und automatisch zur Bring! Einkaufsliste hinzufügt.

## 🎯 Features
- **Wakeword-Erkennung**: Aktivierung durch Custom Wakeword "heyListe" oder Standard "Alexa" (Picovoice Porcupine)
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

### 4. Audio-Geräte konfigurieren
**Wichtig**: Das System muss wissen, welches Audio-Gerät für die Wiedergabe verwendet werden soll.

```bash
# Verfügbare Audio-Geräte anzeigen
aplay -l
```

**Beispiel-Ausgabe:**
```
**** List of PLAYBACK Hardware Devices ****
card 0: Headphones [bcm2835 Headphones], device 0: bcm2835 Headphones
card 1: USB [Jabra SPEAK 510 USB], device 0: USB Audio [USB Audio]
card 2: vc4hdmi0 [vc4-hdmi-0], device 0: MAI PCM i2s-hifi-0
```

**Konfiguration:**
- **USB-Lautsprecher**: Verwende `plughw:1,0` (Card 1, Device 0)
- **HDMI-Audio**: Verwende `plughw:2,0` (Card 2, Device 0)
- **Standard-Kopfhörer**: Verwende `plughw:0,0` (Card 0, Device 0)

### 5. Umgebungsvariablen konfigurieren
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

# Audio-Device Konfiguration
AUDIO_DEVICE=plughw:1,0  # Anpassen an dein Audio-Gerät

# Wakeword-Konfiguration (optional)
# Falls keine Custom-Dateien im src/ Verzeichnis vorhanden sind:
# WAKEWORD_KEYWORD_PATH=/pfad/zu/deinem/wakeword.ppn
# WAKEWORD_MODEL_PATH=/pfad/zu/deinem/sprachmodell.pv
# WAKEWORD_NAME=Alexa  # oder dein gewünschtes Wakeword
```

**Audio-Device-Beispiele:**
- `plughw:1,0` - USB-Lautsprecher (Card 1)
- `plughw:0,0` - Standard-Kopfhörer (Card 0)
- `plughw:2,0` - HDMI-Audio (Card 2)
- `default` - System-Standard

## 🎮 Nutzung

### Starten
```bash
python main.py
```

### Bedienung
1. **Warten**: Das System lauscht kontinuierlich auf das konfigurierte Wakeword (Standard: "heyListe" oder "Alexa")
2. **Aktivieren**: Sage das Wakeword und warte auf das Bestätigungssignal
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
├── utils.py       # Audio-Wiedergabe Utilities
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

### Wakeword-Konfiguration

#### Wakeword-Priorität
Das System verwendet folgende Priorität für Wakewords:

1. **Custom Wakeword-Dateien** (falls vorhanden): `heyListe.ppn` und `PorcupineDe.pv` im `src/` Verzeichnis
2. **Vorgefertigtes Wakeword** (falls in `.env` konfiguriert): Über `WAKEWORD_KEYWORD_PATH` und `WAKEWORD_MODEL_PATH`
3. **Standard "Alexa"** (Fallback): Falls keine Custom-Dateien vorhanden und keine `.env`-Konfiguration

#### Custom Wakeword (empfohlen)
Das System erkennt automatisch Custom Wakeword-Dateien im `src/` Verzeichnis. Die Pfade können in der `.env` angepasst werden:

```env
# Custom Wakeword-Konfiguration
WAKEWORD_KEYWORD_PATH=/pfad/zu/deinem/wakeword.ppn
WAKEWORD_MODEL_PATH=/pfad/zu/deinem/sprachmodell.pv
WAKEWORD_NAME=heyListe  # Anzeigename für das Wakeword
```

**Custom Wakeword erstellen:**
1. Besuche [Picovoice Console](https://console.picovoice.ai/)
2. Gehe zu "Voice Models" → "Create Voice Model"
3. Wähle deine Sprache (z.B. Deutsch)
4. Gehe zu "Custom Keywords" → "Create Custom Keyword"
5. Gib dein gewünschtes Wakeword ein (z.B. "heyListe", "Einkaufsliste", etc.)
6. Lade die `.ppn`-Datei herunter und platziere sie im `src/` Verzeichnis
7. Lade das Sprachmodell (`.pv`-Datei) herunter und platziere es im `src/` Verzeichnis

#### Vorgefertigtes Wakeword verwenden
Falls du ein vorgefertigtes Wakeword verwenden möchtest:

```env
# Vorgefertigtes Wakeword (z.B. "Alexa", "Hey Google", etc.)
WAKEWORD_KEYWORD_PATH=/pfad/zu/vorgefertigtem_wakeword.ppn
WAKEWORD_MODEL_PATH=/pfad/zu/vorgefertigtem_sprachmodell.pv
WAKEWORD_NAME=Alexa  # Anzeigename für das Wakeword
```

**Vorgefertigte Wakewords:**
- **Alexa**: Verwende das "Alexa" Wakeword von Picovoice
- **Hey Google**: Verwende das "Hey Google" Wakeword
- **Hey Siri**: Verwende das "Hey Siri" Wakeword
- **Weitere**: Alle verfügbaren Wakewords findest du in der [Picovoice Console](https://console.picovoice.ai/)

### Bring! Credentials
- Verwende deine normalen Bring! App Login-Daten
- `BRING_LIST_NAME` muss exakt dem Namen deiner Liste in der App entsprechen

## 🛠️ Troubleshooting

### Audio-Probleme
```bash
# Verfügbare Audio-Geräte anzeigen
aplay -l

# Teste Audio-Wiedergabe
aplay -D plughw:1,0 /path/to/test.wav

# Überprüfe Audio-Device in .env
echo $AUDIO_DEVICE
```

**Häufige Audio-Probleme:**
- **"Command returned non-zero exit status 1"**: Falsches Audio-Device in `.env`
- **Kein Ton**: Audio-Device ist belegt oder nicht verfügbar
- **Verzerrter Ton**: Falsche Sample-Rate, versuche `sox` für Resampling

### Bring! API Fehler
- Überprüfe Email/Passwort in `.env`
- Stelle sicher, dass der Listenname exakt übereinstimmt
- Teste die Bring! App auf dem Handy

### Wakeword-Erkennung
- Mikrofon-Berechtigung prüfen
- Spreche das Wakeword deutlich und nicht zu leise
- Teste verschiedene Mikrofon-Positionen
- Überprüfe die Wakeword-Dateien in der `.env`:
  ```bash
  # Teste ob die Dateien existieren
  ls -la $WAKEWORD_KEYWORD_PATH
  ls -la $WAKEWORD_MODEL_PATH
  ```
- Bei Custom Wakewords: Stelle sicher, dass die `.ppn` und `.pv` Dateien korrekt heruntergeladen wurden
- Bei vorgefertigten Wakewords: Verwende die passenden Sprachmodelle für deine Sprache 