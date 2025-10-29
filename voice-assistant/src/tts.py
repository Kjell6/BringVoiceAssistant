import os
import time
import tempfile
import subprocess
from gtts import gTTS
from .utils import play_audio_file
import asyncio

# Piper TTS Modellpfad
PIPER_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'voices', 'Pavoque_low.onnx')


def _cleanup_temp_file(file_path: str):
    """Hilfsfunktion: Löscht temporäre Dateien."""
    if file_path and os.path.exists(file_path):
        try:
            os.unlink(file_path)
        except Exception as e:
            print(f"Warnung: Fehler beim Löschen von {file_path}: {e}")


def _measure_and_log(start_time: float, engine_name: str, text: str):
    """Hilfsfunktion: Misst und loggt die Ausführungszeit."""
    duration = time.time() - start_time
    print(f"{engine_name} Generation für '{text}' dauerte: {duration:.2f}s")


async def generate_tts_async(text: str, lang: str = "de") -> str:
    """
    Generiert TTS-Audio asynchron (Gemini/Google TTS).
    Gibt den Pfad zur Audio-Datei zurück, spielt aber nicht ab.
    
    Ideal für Parallelisierung - TTS läuft während andere Prozesse laufen.
    
    Args:
        text: Text zum Synthetisieren
        lang: Sprachcode (Standard: 'de')
    
    Returns:
        Pfad zur generierten MP3-Datei oder None bei Fehler
    """
    if not text:
        print("[yellow]Fehler: Leerer Text übergeben[/yellow]")
        return None
    
    mp3_path = None
    start_time = time.time()
    
    try:
        # Erstelle MP3 und speichere (blockierende Arbeit in Thread auslagern)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            mp3_path = tmp.name

        def _save_gtts(path: str, t: str, l: str):
            gTTS(text=t, lang=l).save(path)

        await asyncio.to_thread(_save_gtts, mp3_path, text, lang)
        
        duration = time.time() - start_time
        print(f"[dim]🔊 TTS generiert ('{text[:30]}...'): {duration:.2f}s[/dim]")
        
        return mp3_path
    
    except Exception as e:
        print(f"[red]Fehler bei TTS-Generierung: {e}[/red]")
        if mp3_path and os.path.exists(mp3_path):
            try:
                os.unlink(mp3_path)
            except:
                pass
        return None


def speak(text: str, lang: str = "de"):
    """
    Google Text-to-Speech (gTTS).
    
    Args:
        text: Text zum Synthetisieren
        lang: Sprachcode (Standard: 'de')
    """
    if not text:
        print("Fehler: Leerer Text übergeben")
        return
    
    mp3_path = None
    start_time = time.time()
    
    try:
        # Erstelle MP3 und speichere
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            mp3_path = tmp.name
            gTTS(text=text, lang=lang).save(mp3_path)
        
        # Spiele direkt ab
        play_audio_file(mp3_path)
        _measure_and_log(start_time, "Google TTS", text)
        
    except Exception as e:
        print(f"Fehler bei Google TTS: {e}")
    finally:
        _cleanup_temp_file(mp3_path)


def speakOpenAI(text: str):
    """
    OpenAI-kompatible TTS (z.B. mylab.th-luebeck.dev).
    Optimiert: Spielt MP3 direkt ab ohne Konvertierung.
    
    Args:
        text: Text zum Synthetisieren
    """
    if not text:
        print("Fehler: Leerer Text übergeben")
        return
    
    mp3_path = None
    start_time = time.time()
    
    try:
        from openai import OpenAI
        
        # Initialisiere Client
        client = OpenAI(
            base_url="https://models.mylab.th-luebeck.dev/v1",
            api_key="-"
        )
        
        # Erstelle MP3 und speichere
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            mp3_path = tmp.name
            response = client.audio.speech.create(
                model="tts-1-hd",
                voice="onyx",
                speed=1.1,
                input=text
            )
            response.stream_to_file(mp3_path)
        
        # Spiele direkt ab
        play_audio_file(mp3_path)
        _measure_and_log(start_time, "OpenAI TTS", text)
        
    except ImportError:
        print("Fehler: openai Paket nicht installiert (pip install openai)")
    except Exception as e:
        print(f"Fehler bei OpenAI TTS: {e}")
    finally:
        _cleanup_temp_file(mp3_path)


def speakPiper(text: str):
    """
    Piper TTS (lokal, offline).
    
    Args:
        text: Text zum Synthetisieren
    """
    if not text:
        print("Fehler: Leerer Text übergeben")
        return
    
    if not os.path.exists(PIPER_MODEL_PATH):
        print(f"Fehler: Piper Modell nicht gefunden: {PIPER_MODEL_PATH}")
        return
    
    output_path = None
    start_time = time.time()
    
    try:
        # Erstelle WAV Datei
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name
        
        # Synthetisiere mit Piper
        subprocess.run(
            ["piper", "--model", PIPER_MODEL_PATH, "--output_file", output_path],
            input=text,
            encoding='utf-8',
            check=True,
            capture_output=True
        )
        
        # Spiele ab
        play_audio_file(output_path)
        _measure_and_log(start_time, "Piper TTS", text)
        
    except FileNotFoundError:
        print("Fehler: Piper nicht installiert oder Modell/Audio-Player nicht gefunden")
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei Piper Synthese: {e}")
    except Exception as e:
        print(f"Fehler bei Piper TTS: {e}")
    finally:
        _cleanup_temp_file(output_path)
