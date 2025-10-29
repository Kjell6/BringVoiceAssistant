import os
from dotenv import load_dotenv
from src.wakeword import listen_for_wakeword
from src.gemini import extract_shopping_list_from_audio
from src.tts import speak
from src.config import AudioConfig
from src.utils import play_audio_file
from rich import print
import sounddevice as sd
import scipy.io.wavfile as wav
import io
import asyncio
import aiohttp
from bring_api import Bring

load_dotenv()

# Konstanten
RECORDING_DURATION = 5
SAMPLE_RATE = 16000
LAST_RECORDING_FILE = "last_recording.wav"
SIGNAL_START = "signal.wav"
SIGNAL_END = "signalAus.wav"


def _format_item_display(item: dict) -> str:
    """Formatiert einen Artikel für die Konsolenausgabe."""
    spec = f" ({item.get('specification')})" if item.get('specification') else ""
    return f"{item.get('name')}{spec}"


def _format_items_for_speech(items: list) -> str:
    """Formatiert Artikel-Liste für Sprachausgabe (z.B. 'Milch, Brot und Eier')."""
    if not items:
        return ""
    
    names = []
    for item in items:
        name = item.get('name', '')
        spec = f" {item.get('specification')}" if item.get('specification') else ""
        names.append(f"{name}{spec}")
    
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f" und {names[-1]}"


def _play_signal(file_path: str):
    """Spielt ein Audio-Signal ab."""
    try:
        play_audio_file(file_path)
    except FileNotFoundError:
        print(f"[yellow]Signal nicht gefunden: {file_path}[/yellow]")
    except Exception as e:
        print(f"[yellow]Fehler beim Abspielen: {e}[/yellow]")


def record_audio(duration: int = RECORDING_DURATION, samplerate: int = SAMPLE_RATE) -> bytes:
    """
    Zeichnet Audio vom Mikrofon auf.
    
    Args:
        duration: Aufnahmedauer in Sekunden
        samplerate: Sample-Rate in Hz
    
    Returns:
        Audio-Daten als WAV-Bytes
    """
    print("[cyan]Bitte sprich deine Einkaufsliste nach dem Signal.[/cyan]")
    
    # Startsignal
    _play_signal(SIGNAL_START)
    sd.wait()
    
    # Aufnahme vom Mikrofon
    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype='int16',
        device=AudioConfig.SOUNDDEVICE_MICROPHONE_INDEX
    )
    sd.wait()
    print("[green]Audioaufnahme beendet.[/green]")
    
    # Endsignal
    _play_signal(SIGNAL_END)
    
    # Konvertiere zu WAV-Bytes
    buf = io.BytesIO()
    wav.write(buf, samplerate, audio)
    audio_bytes = buf.getvalue()
    
    # Speichere zur Überprüfung
    with open(LAST_RECORDING_FILE, "wb") as f:
        f.write(audio_bytes)
    
    return audio_bytes


async def add_items_to_bring(items: list):
    """
    Fügt Artikel zur Bring! Einkaufsliste hinzu.
    
    Args:
        items: Liste mit Artikeln [{name: ..., specification: ...}]
    """
    bring_email = os.getenv("BRING_EMAIL")
    bring_password = os.getenv("BRING_PASSWORD")
    
    if not bring_email or not bring_password:
        print("[red]Bring! Anmeldeinformationen nicht in .env gefunden.[/red]")
        speak("Fehler bei den Anmeldedaten.")
        return
    
    print("[cyan]Verbinde mit Bring! API...[/cyan]")
    
    try:
        async with aiohttp.ClientSession() as session:
            bring = Bring(session, bring_email, bring_password)
            await bring.login()
            
            # Lade Listen
            list_response = await bring.load_lists()
            lists = list_response.lists
            
            if not lists:
                print("[red]Keine Einkaufslisten gefunden.[/red]")
                speak("Fehler beim Laden der Listen.")
                return
            
            # Verwende erste Liste
            shopping_list = lists[0]
            print(f"[cyan]Füge Artikel zur Liste '{shopping_list.name}' hinzu...[/cyan]")
            
            # Füge Artikel einzeln hinzu
            for item in items:
                item_name = item.get('name')
                if not item_name:
                    continue
                
                specification = item.get('specification', '')
                await bring.save_item(shopping_list.listUuid, item_name, specification)
                
                spec_info = f" mit '{specification}'" if specification else ""
                print(f"- [green]{item_name}{spec_info}[/green]")
            
            print("[bold green]Alle Artikel hinzugefügt![/bold green]")
            
            # Vorlesen hinzugefügter Artikel
            speech_text = _format_items_for_speech(items)
            if speech_text:
                speak(f"Ok, ich habe {speech_text} hinzugefügt")
    
    except Exception as e:
        print(f"[red]Fehler mit Bring! API: {e}[/red]")
        speak("Verbindungsfehler.")


def main():
    """Hauptschleife des Sprachassistenten."""
    print("[bold green]Einkaufslisten-Sprachassistent gestartet![/bold green]")
    
    while True:
        print("[yellow]Warte auf Wakeword...[/yellow]")
        listen_for_wakeword()
        
        # Aufnahme
        audio_bytes = record_audio()
        
        # Extrahiere Artikel aus Audio
        items = extract_shopping_list_from_audio(audio_bytes)
        
        if not items:
            print("[yellow]Keine Artikel erkannt.[/yellow]")
            continue
        
        # Zeige erkannte Artikel
        print("[bold blue]Erkannte Artikel:[/bold blue]")
        for item in items:
            print(f"- {_format_item_display(item)}")
        
        # Füge zu Bring! hinzu
        asyncio.run(add_items_to_bring(items))


if __name__ == "__main__":
    main()