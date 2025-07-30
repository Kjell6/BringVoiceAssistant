import tempfile
import platform
import subprocess
import os
from dotenv import load_dotenv

# Lade .env-Datei
load_dotenv()

def play_audio_file(audio_path: str):
    """
    Spielt eine Audiodatei plattformübergreifend ab (macOS, Linux).
    Bei Linux wird versucht, mit sox zu resamplen, ansonsten direkte Wiedergabe.
    Args:
        audio_path (str): Pfad zur abzuspielenden Audiodatei
    """
    system = platform.system()
    resampled_path = None
    
    # Audio-Device aus .env oder Fallback
    audio_device = os.getenv('AUDIO_DEVICE', 'plughw:1,0')
    
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", audio_path], check=True, capture_output=True)
        elif system == "Linux":
            resampled_path = tempfile.NamedTemporaryFile(suffix="_48k.wav", delete=False).name
            try:
                subprocess.run([
                    "sox",
                    audio_path,
                    "-r", "48000",
                    "-c", "2",
                    "-b", "16",
                    resampled_path,
                ], check=True, capture_output=True)
                subprocess.run(["aplay", "-D", audio_device, resampled_path], check=True, capture_output=True)
            except FileNotFoundError:
                subprocess.run(["aplay", "-D", audio_device, audio_path], check=True, capture_output=True)
        else:
            print(f"Warnung: Kein Audio-Player für Betriebssystem '{system}' gefunden.")
    finally:
        if resampled_path and os.path.exists(resampled_path):
            try:
                os.unlink(resampled_path)
            except Exception as cleanup_error:
                print(f"Warnung: Fehler beim Aufräumen temporärer Dateien: {cleanup_error}")