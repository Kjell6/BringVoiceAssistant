import os
import io
import wave
import subprocess
import time
import tempfile
import platform
# from piper import PiperVoice # No longer used directly for synthesis

# Pfad zum Piper-Sprachmodell. Geht vom 'src'-Ordner eine Ebene nach oben
# und dann in den 'voices'-Ordner.
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'voices', 'Pavoque_low.onnx')

def _check_model_path():
    """Überprüft, ob das Sprachmodell existiert."""
    if not os.path.exists(MODEL_PATH):
        print(f"Fehler: Sprachmodell nicht gefunden unter: {MODEL_PATH}")
        return False
    return True

def speak(text: str):
    """
    Wandelt Text mit Piper in Sprache um und spielt sie ab.
    Nutzt den gleichen Ansatz wie die Signal-Wiedergabe für bessere Fehlerbehandlung.
    """
    if not text:
        print("Speak-Funktion erhielt leeren Text.")
        return

    if not _check_model_path():
        return

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
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", output_path], check=True, capture_output=True)
        elif system == "Linux":  # Raspberry Pi, etc.
            # Erstelle temporäre resampelte Datei (wie bei play_signal)
            resampled_path = tempfile.NamedTemporaryFile(suffix="_48k.wav", delete=False).name
            try:
                # Resample mit sox für bessere Qualität
                subprocess.run([
                    "sox",
                    output_path,
                    "-r", "48000",
                    "-c", "2",
                    "-b", "16",
                    resampled_path,
                ], check=True, capture_output=True)
                subprocess.run(["aplay", "-D", "plughw:3,0", resampled_path], check=True, capture_output=True)
            except FileNotFoundError:
                # sox nicht verfügbar → direkte Wiedergabe
                subprocess.run(["aplay", "-D", "plughw:3,0", output_path], check=True, capture_output=True)
        else:
            print(f"Warnung: Kein Audio-Player für Betriebssystem '{system}' gefunden.")
            return
            
        print(f"Audio für '{text}' erfolgreich abgespielt.")

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


# Überprüfe den Modellpfad beim Start.
_check_model_path()
