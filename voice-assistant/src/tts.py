import os
import io
import wave
import subprocess
import time
import tempfile
import platform
# from piper import PiperVoice # No longer used directly for synthesis
from gtts import gTTS
from .utils import play_audio_file

# Pfad zum Piper-Sprachmodell. Geht vom 'src'-Ordner eine Ebene nach oben
# und dann in den 'voices'-Ordner.
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'voices', 'Pavoque_low.onnx')

def _check_model_path():
    """Überprüft, ob das Sprachmodell existiert."""
    if not os.path.exists(MODEL_PATH):
        print(f"Fehler: Sprachmodell nicht gefunden unter: {MODEL_PATH}")
        return False
    return True

def speakPiper(text: str):
    """
    Wandelt Text mit Piper in Sprache um und spielt sie ab.
    Nutzt den gleichen Ansatz wie die Signal-Wiedergabe für bessere Fehlerbehandlung.
    
    Args:
        text (str): Der zu synthetisierende Text
    """
    if not text:
        print("Speak-Funktion erhielt leeren Text.")
        return

    if not _check_model_path():
        return
        
    start_time = time.time()

    output_path = None
    resampled_path = None
    try:
        # Erstelle eine temporäre WAV-Datei
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            output_path = tmp_file.name

        # Synthetisiere Audio über das Piper-Kommandozeilen-Tool
        piper_command = [
            "piper",
            "--model",
            MODEL_PATH,
            "--output_file",
            output_path,
        ]
        subprocess.run(
            piper_command,
            input=text,
            encoding='utf-8',
            check=True,
            capture_output=True
        )

        # Audio-Wiedergabe mit dem gleichen Ansatz wie bei Signal-Sounds
        try:
            play_audio_file(output_path)
        except Exception as e:
            print(f"Fehler bei der Audio-Wiedergabe: {e}")
            
        end_time = time.time()
        duration = end_time - start_time
        print(f"TTS Generation für '{text}' dauerte: {duration:.2f} Sekunden")

    except FileNotFoundError as e:
        print(f"Audiodatei oder Player nicht gefunden: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Ausführen des Audio-Befehls: {e}")
    except Exception as e:
        print(f"Fehler bei der Sprachsynthese oder Wiedergabe: {e}")
    finally:
        # Aufräumen der temporären Dateien
        try:
            if output_path and os.path.exists(output_path):
                os.unlink(output_path)
            if resampled_path and os.path.exists(resampled_path):
                os.unlink(resampled_path)
        except Exception as cleanup_error:
            print(f"Warnung: Fehler beim Aufräumen temporärer Dateien: {cleanup_error}")


def speak(text: str, lang: str = "de"):
    """
    Wandelt Text mit Google Text-to-Speech (gTTS) in Sprache um und spielt sie ab.
    Args:
        text (str): Der zu synthetisierende Text
        lang (str): Sprachcode (Standard: 'de')
    """
    import tempfile
    import os
    try:
        if not text:
            print("gspeak-Funktion erhielt leeren Text.")
            return
        # Erzeuge temporäre MP3-Datei
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tts = gTTS(text=text, lang=lang)
            tts.save(tmp_file.name)
            mp3_path = tmp_file.name
        # Konvertiere MP3 zu WAV für play_audio_file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_path = wav_file.name
        # Nutze ffmpeg zur Umwandlung
        import subprocess
        subprocess.run(["ffmpeg", "-y", "-i", mp3_path, wav_path], check=True, capture_output=True)
        play_audio_file(wav_path)
    except Exception as e:
        print(f"Fehler bei gspeak: {e}")
    finally:
        # Aufräumen
        try:
            if 'mp3_path' in locals() and os.path.exists(mp3_path):
                os.unlink(mp3_path)
            if 'wav_path' in locals() and os.path.exists(wav_path):
                os.unlink(wav_path)
        except Exception as cleanup_error:
            print(f"Warnung: Fehler beim Aufräumen temporärer Dateien: {cleanup_error}")


# Überprüfe den Modellpfad beim Start.
_check_model_path()
