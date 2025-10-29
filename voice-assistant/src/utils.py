import platform
import subprocess
import tempfile
import os

def play_audio_file(audio_path: str):
    """
    Intelligente Audio-Wiedergabe: WAV/MP3 direkt abspielen ohne unnötige Konvertierung.
    
    Strategie:
    - WAV: aplay direkt (schnell, Standard auf Linux)
    - MP3: mpg123 → ffplay → (aplay mit Konvertierung)
    - Andere: ffplay → aplay mit Konvertierung
    
    Args:
        audio_path: Pfad zur abzuspielenden Audiodatei
    """
    system = platform.system()
    file_ext = os.path.splitext(audio_path)[1].lower()
    
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", audio_path], check=True, capture_output=True)
        
        elif system == "Linux":
            # WAV-Dateien: Direktes aplay (schnell, Standard)
            if file_ext == ".wav":
                try:
                    subprocess.run(["aplay", audio_path], check=True, capture_output=True, timeout=60)
                    return
                except FileNotFoundError:
                    pass  # aplay nicht vorhanden, versuche ffplay
            
            # MP3-Dateien: mpg123 zuerst (schnellster MP3-Player)
            if file_ext == ".mp3":
                try:
                    subprocess.run(["mpg123", "-q", audio_path], check=True, capture_output=True, timeout=60)
                    return
                except (FileNotFoundError, subprocess.CalledProcessError):
                    pass  # mpg123 nicht vorhanden oder fehlgeschlagen
            
            # Fallback: ffplay (breit unterstützt, viele Formate)
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
            
            # Letzter Fallback: aplay mit ffmpeg Konvertierung (nur wenn nötig)
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
            print(f"Warnung: Kein Audio-Player für '{system}' verfügbar.")
    
    except FileNotFoundError:
        print(f"Fehler: Audio-Player nicht gefunden.")
    except subprocess.TimeoutExpired:
        print("Fehler: Audio-Wiedergabe hat zu lange gedauert.")
    except Exception as e:
        print(f"Fehler beim Abspielen der Audiodatei: {e}")