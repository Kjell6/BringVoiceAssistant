# BringVoiceAssistant - Sprachgesteuerter Einkaufslisten-Assistent 🛒

Ein intelligenter Sprachassistent für Raspberry Pi, der auf dein Custom Wakeword "heyListe" hört, deine gesprochenen Einkaufswünsche versteht und automatisch zur Bring! Einkaufsliste hinzufügt.

## ✨ Features

- **🎤 Wakeword-Erkennung**: Custom Wakeword "heyListe" oder Standard-Wakewords wie "Alexa" (Picovoice Porcupine)
- **🗣️ Spracherkennung**: Hochwertige Audioaufnahme und Transkription deiner Einkaufswünsche
- **🤖 KI-Analyse**: Intelligente Extraktion von Einkaufsartikeln mit Google Gemini 2.5 Flash
- **📱 Bring! Integration**: Automatisches Hinzufügen zur Bring! Einkaufsliste
- **🔊 Audio-Feedback**: Sprachbestätigung der hinzugefügten Artikel
- **⏱️ Dauerbetrieb**: Kontinuierliches Lauschen auf Wakeword
- **⚙️ Zentrale Konfiguration**: Alle Audiogeräte-Einstellungen an einer Stelle

## 🚀 Schnellstart

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

### 4. Audiogeräte identifizieren

Bevor du die Konfiguration einrichtest, musst du die richtigen Geräte-Indizes für dein System finden:

**Für Sounddevice (Audioaufnahme mit Mikrofon):**
```bash
source venv/bin/activate
python3 -c "import sounddevice; print(sounddevice.query_devices())"
```

**Für PvRecorder (Wakeword-Erkennung):**
```bash
source venv/bin/activate
python3 -c "from pvrecorder import PvRecorder; print(PvRecorder.get_available_devices())"
```

**Für ALSA (Audioausgabe / Lautsprecher):**
```bash
aplay -l
```

### 5. `.env`-Datei konfigurieren

Erstelle eine `.env`-Datei im `voice-assistant` Verzeichnis mit deinen Einstellungen:

```env
# ============================================
# API CREDENTIALS
# ============================================

# Google Gemini API
GEMINI_API_KEY=dein_gemini_api_key

# Bring! API Credentials
BRING_EMAIL=deine_bring_email
BRING_PASSWORD=dein_bring_passwort
BRING_LIST_NAME=Zuhause

# Picovoice Access Key (für Wakeword-Erkennung)
PICOVOICE_ACCESS_KEY=dein_picovoice_key

# ============================================
# AUDIO-GERÄTE KONFIGURATION (zentral)
# ============================================

# Sounddevice Mikrofonindex (für Audioaufnahme)
# Beispiel: 0 = Jabra SPEAK 510 USB
SOUNDDEVICE_MICROPHONE_INDEX=0

# PvRecorder Geräteindex (für Wakeword-Erkennung)
# Beispiel: 3 = Jabra SPEAK 510 USB
PVRECORDER_DEVICE_INDEX=3

# ALSA Audioausgabegerät (für Lautsprecher/Signaltöne)
# Beispiele: hw:0,0 (Jabra), default, plughw:0,0
ALSA_AUDIO_DEVICE=hw:0,0
```

## 🎮 Bedienung

### Starten
```bash
cd voice-assistant
source venv/bin/activate
python main.py
```

### Nutzung
1. **Warten**: Das System lauscht kontinuierlich auf das Wakeword "heyListe"
2. **Aktivieren**: Sage "heyListe" und warte auf das Bestätigungssignal
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

## 🔧 Konfiguration im Detail

### Audiogeräte-Konfiguration

Die Audiogeräte werden in einer **zentralen Konfigurationsdatei** verwaltet (`src/config.py`). Alle Einstellungen werden aus der `.env` geladen.

**Warum drei verschiedene Indizes?**
- Jede Bibliothek (sounddevice, pvrecorder, ALSA) zählt die Geräte unterschiedlich
- `src/config.py` koordiniert diese und bietet eine einheitliche Schnittstelle
- **Vorteil**: Du änderst alles nur an einer Stelle in der `.env`!

### Beispiel: Jabra SPEAK 510 USB
```env
# Diese Werte funktionieren für ein Jabra SPEAK 510 USB Mikrofon
SOUNDDEVICE_MICROPHONE_INDEX=0      # Index in sounddevice.query_devices()
PVRECORDER_DEVICE_INDEX=3            # Index in PvRecorder.get_available_devices()
ALSA_AUDIO_DEVICE=hw:0,0            # Ergebnis aus aplay -l
```

## 🏗️ Architektur

```
voice-assistant/
├── main.py                 # Haupteinstiegspunkt
├── requirements.txt        # Python Dependencies
├── .env                    # Konfigurationsdatei
├── src/
│   ├── config.py          # 🆕 Zentrale Audiogeräte-Konfiguration
│   ├── wakeword.py        # Picovoice Wakeword-Erkennung
│   ├── gemini.py          # Gemini API Integration
│   ├── tts.py             # Text-to-Speech Feedback
│   ├── utils.py           # Audio-Wiedergabe Utilities
│   ├── heyListe.ppn       # Custom Wakeword (Deutsch)
│   └── PorcupineDe.pv     # Deutsches Sprachmodell
├── signal.wav             # Aktivierungssignal
└── signalAus.wav          # Deaktivierungssignal
```

### Wichtige Module

| Modul | Funktion |
|-------|----------|
| `config.py` | ⚙️ Zentrale Audiogeräte-Konfiguration aus `.env` |
| `wakeword.py` | 🎤 Hört auf Wakeword und aktiviert Aufnahme |
| `gemini.py` | 🤖 Analysiert Audio und extrahiert Artikel |
| `tts.py` | 🔊 Sprachausgabe der Bestätigungen |
| `utils.py` | 🎵 Audio-Wiedergabe und Geräte-Management |

## 🏠 Deployment auf Raspberry Pi

### Hardware-Anforderungen
- Raspberry Pi 3B+ oder neuer (empfohlen: Pi Zero 2 W oder Pi 4)
- USB-Mikrofon oder Audio-HAT (z.B. Jabra SPEAK 510)
- Lautsprecher oder Kopfhörer
- Stabile Internetverbindung (für APIs)

### Installation

```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python und Audio-Tools installieren
sudo apt install python3-pip python3-venv portaudio19-dev alsa-utils sox -y

# Projekt klonen und Setup
git clone <repository-url>
cd BringVoiceAssistant/voice-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Audiogeräte identifizieren und .env konfigurieren
python3 -c "import sounddevice; print(sounddevice.query_devices())"
python3 -c "from pvrecorder import PvRecorder; print(PvRecorder.get_available_devices())"
aplay -l

# Test starten
python3 main.py
```

### Autostart mit systemd

Erstelle eine Service-Datei für Autostart:

```bash
sudo nano /etc/systemd/system/voice-assistant.service
```

```ini
[Unit]
Description=BringVoiceAssistant - Sprachgesteuerter Einkaufslisten-Assistent
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/BringVoiceAssistant/voice-assistant
Environment=PATH=/home/pi/BringVoiceAssistant/voice-assistant/venv/bin
ExecStart=/home/pi/BringVoiceAssistant/voice-assistant/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Aktiviere und starte den Service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable voice-assistant.service
sudo systemctl start voice-assistant.service

# Status prüfen
sudo systemctl status voice-assistant.service

# Logs anzeigen
sudo journalctl -u voice-assistant.service -f
```

## 🔑 API-Keys erhalten

### Google Gemini API
1. Besuche [Google AI Studio](https://aistudio.google.com/)
2. Klicke auf "Create API Key"
3. Wähle oder erstelle ein Projekt
4. Kopiere deinen API-Key
5. Füge ihn als `GEMINI_API_KEY` in deine `.env` ein

### Picovoice Access Key
1. Registriere dich kostenlos bei [Picovoice Console](https://console.picovoice.ai/)
2. Gehe zu "AccessKey" und erstelle einen neuen
3. Kopiere deinen Access Key
4. Füge ihn als `PICOVOICE_ACCESS_KEY` in deine `.env` ein

### Bring! Credentials
- Verwende deine normalen Bring! App Login-Daten
- `BRING_LIST_NAME` muss exakt dem Namen deiner Liste in der App entsprechen

## 🆕 Wakeword-Konfiguration

### Custom Wakeword verwenden (Standard)

Das System ist bereits mit dem Custom Wakeword **"heyListe"** (Deutsch) konfiguriert. Die benötigten Dateien sind vorhanden:
- `src/heyListe.ppn` - Wakeword-Datei
- `src/PorcupineDe.pv` - Deutsches Sprachmodell

**Keine zusätzliche Konfiguration nötig!** 🎉

### Vorgefertigtes Wakeword verwenden (z.B. "Alexa")

Falls du ein Standard-Wakeword wie "Alexa" bevorzugst:

```bash
# Entferne die Custom-Dateien
rm voice-assistant/src/heyListe.ppn
rm voice-assistant/src/PorcupineDe.pv
```

Das System wechselt automatisch zu "Alexa". Optional kannst du die `.env` konfigurieren:

```env
# Vorgefertigtes Wakeword (in .env, optional)
WAKEWORD_KEYWORD=alexa
WAKEWORD_NAME=Alexa
```

**Verfügbare vorgefertigte Wakewords:**
- `alexa` - Alexa Wakeword
- `hey google` - Google Wakeword  
- `hey siri` - Siri Wakeword
- `computer` - Computer Wakeword
- `jarvis` - Jarvis Wakeword
- Weitere findest du in der [Picovoice Dokumentation](https://picovoice.ai/docs/quick-start/porcupine-c/)

### Eigenes Custom Wakeword erstellen

1. Besuche [Picovoice Console](https://console.picovoice.ai/)
2. Gehe zu "Custom Keywords" → "Create Custom Keyword"
3. Wähle deine Sprache (z.B. Deutsch)
4. Gib dein gewünschtes Wakeword ein (z.B. "Einkaufen", "Shopping", etc.)
5. Lade die `.ppn`-Datei herunter
6. Lade das Sprachmodell (`.pv`-Datei) herunter
7. Kopiere beide Dateien in den `src/` Verzeichnis
8. Benenne die `.ppn`-Datei entsprechend um (z.B. `einkaufen.ppn`)
9. Keine `.env`-Änderungen nötig, das System erkennt die neuen Dateien automatisch

## 🐛 Troubleshooting

### Audio-Probleme

**Symptom**: "Command returned non-zero exit status 1"

```bash
# Schritt 1: Audiogeräte überprüfen
aplay -l                              # Verfügbare Ausgabegeräte
arecord -l                            # Verfügbare Eingabegeräte

# Schritt 2: Richtigen Index finden
python3 -c "import sounddevice; print(sounddevice.query_devices())"

# Schritt 3: Audio-Test
aplay -D hw:0,0 signal.wav           # Mit deinem Gerät testen
```

**Häufige Ursachen:**
- ❌ Falsches ALSA-Gerät in `ALSA_AUDIO_DEVICE`
- ❌ Audio-Gerät ist belegt oder nicht verfügbar
- ❌ Falscher Index in den Konfigurationsvariablen
- ✅ **Lösung**: Überprüfe alle Indizes nochmal und aktualisiere `.env`

### Mikrofon-Probleme

**Symptom**: Wakeword wird nicht erkannt

```bash
# Schritt 1: Verfügbare Eingabegeräte checken
python3 -c "from pvrecorder import PvRecorder; print(PvRecorder.get_available_devices())"

# Schritt 2: Geräteindex überprüfen
# Der richtige Index sollte dein Mikrofon enthalten (z.B. "Jabra SPEAK 510 USB")

# Schritt 3: Versuche mit Standardgerät
# Änder PVRECORDER_DEVICE_INDEX=1 (Default-Gerät) in der .env
```

**Tipps:**
- Spreche das Wakeword **deutlich und mit normaler Lautstärke**
- Versuche verschiedene Mikrofon-Positionen
- Überprüfe, ob die `.ppn` und `.pv` Dateien im `src/` Verzeichnis vorhanden sind
- Teste mit einem anderen Wakeword (z.B. "Alexa")

### Bring! API Fehler

```bash
# Überprüfe Login-Daten
grep "BRING" voice-assistant/.env

# Stelle sicher:
# 1. Email und Passwort sind korrekt
# 2. Der Listenname entspricht exakt der Bring! App
# 3. Internet-Verbindung funktioniert
```

### Logs prüfen

```bash
# Bei systemd Service
sudo journalctl -u voice-assistant.service -f

# Direkter Start (für Debugging)
cd voice-assistant
source venv/bin/activate
python main.py
```

## 📊 Performance & Tipps

### Für Raspberry Pi Zero 2 W
- Nutze den kostenlosen Tier von Gemini (ausreichend)
- Erwäge, die Aufnahmedauer zu reduzieren (`duration=3` statt `5`)
- Verwende ein USB-Mikrofon für bessere Performance

### Für Raspberry Pi 4/5
- Alle Funktionen funktionieren optimal
- Du kannst mit mehr Artikeln pro Session arbeiten

### Netzwerk-Tipps
- Nutze **Wired Ethernet** (stabiler als WiFi)
- Bei WiFi: Verwende 5GHz Band falls möglich
- Google Gemini API benötigt Internetverbindung für KI-Analyse

## 📝 Lizenz

Dieses Projekt ist MIT lizenziert. Siehe LICENSE-Datei für Details.
