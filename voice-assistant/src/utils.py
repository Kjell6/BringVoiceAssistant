import platform
import subprocess
import tempfile
import os

def play_audio_file(audio_path: str):
    """
    Optimierte Audio-Wiedergabe: Spielt MP3/OGG/WAV direkt ab ohne unnötige Konvertierung.
    Unterstützt mehrere Player-Optionen mit intelligenter Fallback-Chain.
    
    Priorität:
    1. mpg123 (schnellster MP3-Player)
    2. ffplay (breit unterstützt)
    3. aplay mit ffmpeg Konvertierung (Fallback)
    
    Args:
        audio_path (str): Pfad zur abzuspielenden Audiodatei
    """
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", audio_path], check=True, capture_output=True)
        elif system == "Linux":
            # Versuche mpg123 zuerst (MP3, schnell)
            try:
                subprocess.run(["mpg123", "-q", audio_path], check=True, capture_output=True, timeout=60)
                return
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
            
            # Fallback: ffplay (auch schnell, breit unterstützt)
            try:
                subprocess.run(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", audio_path],
                    check=True,
                    capture_output=True,
                    timeout=60
                )
                return
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
            
            # Letzter Fallback: aplay (standardmäßig verfügbar, aber nur WAV/PCM)
            # Für MP3 konvertieren
            wav_path = None
            try:
                wav_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
                subprocess.run(
                    ["ffmpeg", "-y", "-i", audio_path, "-acodec", "pcm_s16le", "-ar", "48000", wav_path],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
                subprocess.run(["aplay", wav_path], check=True, capture_output=True, timeout=60)
            finally:
                if wav_path and os.path.exists(wav_path):
                    os.unlink(wav_path)
        else:
            print(f"Warnung: Kein Audio-Player für Betriebssystem '{system}' gefunden.")
    except FileNotFoundError:
        print(f"Fehler: Audio-Player nicht gefunden.")
    except subprocess.TimeoutExpired:
        print("Fehler: Audio-Wiedergabe hat zu lange gedauert.")
    except Exception as e:
        print(f"Fehler beim Abspielen der Audiodatei: {e}")