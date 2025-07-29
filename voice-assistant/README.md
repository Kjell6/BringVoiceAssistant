# Einkaufslisten-Sprachassistent

Ein dauerhaft laufendes Python-Skript, das auf ein Wakeword lauscht, Sprache transkribiert, an Gemini 2.5 Flash sendet und eine formatierte Einkaufsliste im Terminal ausgibt.

## Features
- Wakeword-Erkennung mit Picovoice Porcupine
- Spracheingabe nach Wakeword
- Transkription der Spracheingabe
- Anfrage an Gemini 2.5 Flash (via API)
- Extraktion von Einkaufsartikeln aus Text durch das LLM
- Ausgabe der Einkaufsliste im Terminal

## Setup
1. Repository klonen
2. Virtuelle Umgebung erstellen und aktivieren:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. `.env`-Datei mit API-Keys anlegen (siehe `.env`-Beispiel)

## Nutzung
```bash
python main.py
```

## Deployment auf Raspberry Pi
- Code übertragen (z.B. via Git, SCP oder USB)
- Setup wie oben durchführen
- Optional: Autostart via systemd oder tmux 