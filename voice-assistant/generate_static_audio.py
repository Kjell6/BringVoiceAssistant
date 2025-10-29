#!/usr/bin/env python3
"""
Generiert statische Audio-Dateien die einmalig erstellt und dann wiederverwendet werden.
Läuft einmalig beim Setup, spart Performance bei 24/7 Betrieb.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from src.tts import speak

load_dotenv()

# Erstelle audio Verzeichnis falls nicht vorhanden
AUDIO_DIR = Path(__file__).parent / "src" / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

# Definiere statische Audio-Dateien
STATIC_AUDIO = {
    "no_items_added.mp3": "Nichts auf die Liste gesetzt.",
}

print("[*] Generiere statische Audio-Dateien...\n")

for filename, text in STATIC_AUDIO.items():
    filepath = AUDIO_DIR / filename
    
    # Überspringe wenn bereits vorhanden
    if filepath.exists():
        print(f"[✓] {filename} existiert bereits ({filepath.stat().st_size} bytes)")
        continue
    
    print(f"[→] Generiere {filename}...")
    print(f"    Text: '{text}'")
    
    # Generiere mit speak() (nutzt gTTS)
    speak(text, lang="de")
    
    # gTTS speichert zu temp Pfad, daher müssen wir es manuell speichern
    # Alternativ: Direkt generate_tts_async nutzen
    import tempfile
    import shutil
    from src.tts import generate_tts_async
    import asyncio
    
    # Generiere async und speichere
    async def generate_and_save():
        audio_file = await generate_tts_async(text, lang="de")
        if audio_file:
            shutil.copy(audio_file, str(filepath))
            print(f"[✓] Gespeichert: {filepath} ({filepath.stat().st_size} bytes)")
            try:
                os.unlink(audio_file)
            except:
                pass
            return True
        return False
    
    success = asyncio.run(generate_and_save())
    if not success:
        print(f"[✗] Fehler beim Generieren von {filename}")
        sys.exit(1)

print("\n[✓] Alle statischen Audio-Dateien generiert!")
print(f"[*] Speicherort: {AUDIO_DIR}")
