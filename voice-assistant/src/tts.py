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
    Optimiert: Spielt MP3 direkt ab ohne Konvertierung zu WAV
    
    Args:
        text (str): Der zu synthetisierende Text
        lang (str): Sprachcode (Standard: 'de')
    """
    if not text:
        print("speak-Funktion erhielt leeren Text.")
        return
    
    mp3_path = None
    start_time = time.time()
    
    try:
        # Erzeuge temporäre MP3-Datei und speichere direkt
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            mp3_path = tmp_file.name
            tts = gTTS(text=text, lang=lang)
            tts.save(mp3_path)
        
        # Spiele MP3 direkt ab (KEINE Konvertierung zu WAV mehr!)
        try:
            play_audio_file(mp3_path)
        except Exception as e:
            print(f"Fehler beim Abspielen der TTS-Ausgabe: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"Google TTS Generation für '{text}' dauerte: {duration:.2f} Sekunden")
            
    except Exception as e:
        print(f"Fehler bei Google TTS: {e}")
    finally:
        # Aufräumen
        try:
            if mp3_path and os.path.exists(mp3_path):
                os.unlink(mp3_path)
        except Exception as cleanup_error:
            print(f"Warnung: Fehler beim Aufräumen temporärer Dateien: {cleanup_error}")


def speakOpenAI(text: str):
    """
    Wandelt Text mit OpenAI-kompatiblen TTS-API in Sprache um und spielt sie ab.
    Funktioniert mit OpenAI und anderen kompatiblen APIs (z.B. mylab.th-luebeck.dev).
    
    Optimiert: Spielt MP3 direkt ab ohne Konvertierung zu WAV
    
    Args:
        text (str): Der zu synthetisierende Text
    """
    if not text:
        print("speakOpenAI-Funktion erhielt leeren Text.")
        return
    
    start_time = time.time()
    mp3_path = None
    
    try:
        from openai import OpenAI
        
        # Initialisiere OpenAI-Client mit benutzerdefinierten Einstellungen
        # Arbeiten Sie nicht mit dem Default Endpunkt von OpenAI sondern mit unserem
        client = OpenAI(
            base_url="https://models.mylab.th-luebeck.dev/v1",
            api_key="-"  # Sie können hier irgendeinen API-KEY angeben, aber keinen leeren!
        )
        
        # Erstelle temporäre MP3-Datei
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            mp3_path = tmp_file.name
        
        # Erstelle TTS-Response und speichere als MP3
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            speed=1.1,
            input=text
        )
        response.stream_to_file(mp3_path)
        
        # Spiele MP3 direkt ab (nutzt optimierte play_audio_file aus utils.py)
        try:
            play_audio_file(mp3_path)
        except Exception as e:
            print(f"Fehler beim Abspielen der TTS-Ausgabe: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"OpenAI TTS Generation für '{text}' dauerte: {duration:.2f} Sekunden")
        
    except ImportError:
        print("Fehler: openai Paket nicht installiert. Bitte 'pip install openai' ausführen.")
    except Exception as e:
        print(f"Fehler bei OpenAI TTS: {e}")
    finally:
        # Aufräumen der temporären Dateien
        try:
            if mp3_path and os.path.exists(mp3_path):
                os.unlink(mp3_path)
        except Exception as cleanup_error:
            print(f"Warnung: Fehler beim Aufräumen temporärer Dateien: {cleanup_error}")


# Überprüfe den Modellpfad beim Start.
_check_model_path()
