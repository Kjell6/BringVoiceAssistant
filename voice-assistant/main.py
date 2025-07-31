import os
from dotenv import load_dotenv
from src.wakeword import listen_for_wakeword
from src.gemini import extract_shopping_list_from_audio
from src.tts import speak
from rich import print
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import subprocess
import tempfile
import io
import requests
import asyncio
import aiohttp
from bring_api import Bring
from src.utils import play_audio_file
import torch
from silero_vad import load_silero_vad, get_speech_timestamps, collect_chunks

load_dotenv()

def record_audio(samplerate=16000, max_duration=15):
    print("[cyan]Bitte sprich deine Einkaufsliste nach dem Signal.Maximal 15 Sekunden.[/cyan]")
    play_signal("signal.wav")

    # Aufnahme für maximal max_duration Sekunden
    audio = sd.rec(int(max_duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    print("[green]Audioaufnahme beendet.[/green]")
    play_signal("signalAus.wav")

    # In float32 umwandeln und normalisieren
    audio_float = audio.flatten().astype('float32') / 32768.0
    audio_tensor = torch.from_numpy(audio_float)

    # Modell laden
    model = load_silero_vad()
    # Sprachsegmente erkennen
    speech_timestamps = get_speech_timestamps(audio_tensor, model, sampling_rate=samplerate)
    # Nur Sprachsegmente extrahieren
    speech_audio = collect_chunks(speech_timestamps, audio_tensor)

    # In WAV-Format umwandeln (Bytes)
    buf = io.BytesIO()
    wav.write(buf, samplerate, (speech_audio.numpy() * 32768).astype('int16'))
    return buf.getvalue()

def main():
    print("[bold green]Einkaufslisten-Sprachassistent gestartet![/bold green]")
    while True:
        print("[yellow]Warte auf Wakeword...[/yellow]")
        listen_for_wakeword()
        audio_bytes = record_audio()
        einkaufsliste = extract_shopping_list_from_audio(audio_bytes)
        # Sende die Liste an die Bring! API
        if einkaufsliste:
            print("[bold blue]Erkannte Artikel:[/bold blue]")
            item_names_for_speak = []
            for item in einkaufsliste:
                spec = f" ({item.get('specification')})" if item.get('specification') else ""
                print(f"- {item.get('name')}{spec}")
                item_names_for_speak.append(f"{item.get('name')}{spec}".strip())

            asyncio.run(add_items_to_bring(einkaufsliste))
        else:
            print("[yellow]Keine Artikel zum Hinzufügen erkannt.[/yellow]")

async def add_items_to_bring(items):
    bring_email = os.getenv("BRING_EMAIL")
    bring_password = os.getenv("BRING_PASSWORD")

    if not bring_email or not bring_password:
        print("[red]Bring! Anmeldeinformationen nicht in .env gefunden.[/red]")
        speak("Fehler bei den Anmeldedaten.")
        return

    print("[cyan]Verbinde mit Bring! API...[/cyan]")
    async with aiohttp.ClientSession() as session:
        try:
            bring = Bring(session, bring_email, bring_password)
            await bring.login()

            list_response = await bring.load_lists()
            lists = list_response.lists
            if not lists:
                print("[red]Keine Einkaufslisten in deinem Bring! Konto gefunden.[/red]")
                speak("Fehler beim Laden der Listen.")
                return

            # Wähle die erste Liste aus
            shopping_list_uuid = lists[0].listUuid
            shopping_list_name = lists[0].name
            print(f"[cyan]Füge Artikel zur Liste '{shopping_list_name}' hinzu...[/cyan]")

            for item in items:
                item_name = item.get('name')
                specification = item.get('specification', '')
                if not item_name: # Überspringe ungültige Einträge
                    continue
                await bring.save_item(shopping_list_uuid, item_name, specification)
                spec_info = f" mit Spezifikation '{specification}'" if specification else ""
                print(f"- [green]'{item_name}'{spec_info} hinzugefügt.[/green]")
            
            print("[bold green]Alle Artikel erfolgreich zu Bring! hinzugefügt.[/bold green]")

            # Erfolgreich hinzugefügte Artikel vorlesen
            item_names_with_specs = []
            for item in items:
                if item.get('name'):
                    spec = f" {item.get('specification')}" if item.get('specification') else ""
                    item_names_with_specs.append(f"{item.get('name')}{spec}")
            
            if item_names_with_specs:
                if len(item_names_with_specs) == 1:
                    added_items_str = item_names_with_specs[0]
                else:
                    all_but_last = ', '.join(item_names_with_specs[:-1])
                    last_item = item_names_with_specs[-1]
                    added_items_str = f"{all_but_last} und {last_item}"
                
                speak(f"Ok, Ich habe, {added_items_str} hinzugefügt")

        except Exception as e:
            print(f"[red]Fehler bei der Verbindung mit Bring!: {e}[/red]")
            speak("Verbindungsfehler.")

def play_signal(file_path):
    """Signalton über USB-Speaker abspielen (48 kHz / plughw:3,0)."""
    try:
        play_audio_file(file_path)
    except FileNotFoundError:
        print("[red]Audiodatei nicht gefunden. Bitte im Projektordner ablegen.[/red]")
    except Exception as e:
        print(f"[red]Fehler beim Abspielen der Audiodatei: {e}[/red]")

if __name__ == "__main__":
    main()
