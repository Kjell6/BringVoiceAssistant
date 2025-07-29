import os
from dotenv import load_dotenv
from src.wakeword import listen_for_wakeword
from src.gemini import extract_shopping_list_from_audio
from rich import print
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import io
import requests
import asyncio
import aiohttp
from bring_api import Bring

load_dotenv()

def record_audio(duration=8, samplerate=16000):
    print("[cyan]Bitte sprich deine Einkaufsliste nach dem Signal.[/cyan]")
    sd.play(np.ones(int(0.2 * samplerate)), samplerate)  # kurzes Signal
    sd.wait()
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    print("[green]Audioaufnahme beendet.[/green]")
    # In WAV-Format umwandeln (Bytes)
    buf = io.BytesIO()
    wav.write(buf, samplerate, audio)
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
            asyncio.run(add_items_to_bring(einkaufsliste))
        else:
            print("[yellow]Keine Artikel zum Hinzufügen erkannt.[/yellow]")
        print("[bold blue]Einkaufsliste:[/bold blue]")
        for item in einkaufsliste:
            print(f"- {item}")

async def add_items_to_bring(items):
    bring_email = os.getenv("BRING_EMAIL")
    bring_password = os.getenv("BRING_PASSWORD")

    if not bring_email or not bring_password:
        print("[red]Bring! Anmeldeinformationen nicht in .env gefunden.[/red]")
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
                return

            # Wähle die erste Liste aus
            shopping_list_uuid = lists[0].listUuid
            shopping_list_name = lists[0].name
            print(f"[cyan]Füge Artikel zur Liste '{shopping_list_name}' hinzu...[/cyan]")

            for item in items:
                await bring.save_item(shopping_list_uuid, item)
                print(f"- [green]'{item}' hinzugefügt.[/green]")
            
            print("[bold green]Alle Artikel erfolgreich zu Bring! hinzugefügt.[/bold green]")

        except Exception as e:
            print(f"[red]Fehler bei der Verbindung mit Bring!: {e}[/red]")

if __name__ == "__main__":
    main()
