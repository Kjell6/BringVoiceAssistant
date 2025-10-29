"""
Zentrale Konfiguration für Audiogeräte und andere Einstellungen.
Alle Geräte-Indizes werden hier aus der .env Datei geladen.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class AudioConfig:
    """Audio-Geräte Konfiguration"""
    
    # Sounddevice (für Python Audioaufnahme)
    SOUNDDEVICE_MICROPHONE_INDEX = int(os.getenv('SOUNDDEVICE_MICROPHONE_INDEX', '0'))
    
    # PvRecorder (für Wakeword-Erkennung)
    PVRECORDER_DEVICE_INDEX = int(os.getenv('PVRECORDER_DEVICE_INDEX', '3'))
    
    # ALSA aplay (für Audioausgabe)
    ALSA_AUDIO_DEVICE = os.getenv('ALSA_AUDIO_DEVICE', 'hw:0,0')
    
    def __repr__(self):
        return (
            f"AudioConfig(\n"
            f"  sounddevice_microphone_index={self.SOUNDDEVICE_MICROPHONE_INDEX}\n"
            f"  pvrecorder_device_index={self.PVRECORDER_DEVICE_INDEX}\n"
            f"  alsa_audio_device={self.ALSA_AUDIO_DEVICE}\n"
            f")"
        )
