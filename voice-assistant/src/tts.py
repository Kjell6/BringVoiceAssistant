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
    Basiert auf der funktionierenden Logik des Benutzers.
    """
    if not text:
        print("Speak-Funktion erhielt leeren Text.")
        return

    if not _check_model_path():
        return

    output_path = None
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

        # Audio-Player je nach Betriebssystem auswählen
        system = platform.system()
        player_command = []
        if system == "Darwin":  # macOS
            player_command = ["afplay", output_path]
        elif system == "Linux":  # Raspberry Pi, etc.
            player_command = ["aplay", output_path]
        
        if player_command:
            subprocess.run(player_command, check=True, capture_output=True)
            print(f"Audio für '{text}' erfolgreich abgespielt.")
        else:
            print(f"Warnung: Kein Audio-Player für Betriebssystem '{system}' gefunden.")

    except Exception as e:
        print(f"Fehler bei der Sprachsynthese oder Wiedergabe: {e}")


# Überprüfe den Modellpfad beim Start.
_check_model_path()
