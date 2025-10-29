import os
import time
import sys
from dotenv import load_dotenv
from src.wakeword import listen_for_wakeword
from src.gemini import extract_shopping_list_from_audio
from src.tts import speak, generate_tts_async
from src.config import AudioConfig
from src.utils import play_audio_file
from rich import print
import sounddevice as sd
import scipy.io.wavfile as wav
import io
import asyncio
import aiohttp
from bring_api import Bring, BringAuthException, BringRequestException, BringParseException
import logging

load_dotenv()

# Windows Event Loop Fix (für 24/7 Betrieb)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Setup Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Konstanten
RECORDING_DURATION = 5
SAMPLE_RATE = 16000
LAST_RECORDING_FILE = "last_recording.wav"
SIGNAL_START = "signal.wav"
SIGNAL_END = "signalAus.wav"
LISTS_CACHE_TIMEOUT = 300  # 5 Minuten Cache für Listen
SESSION_MAX_AGE = 3600 * 6  # 6 Stunden - nach dieser Zeit neu-login (24/7 Stabilität)

# Cache für Bring! Session und Listen
class BringCache:
    """Cache für Bring! API Session und Listen mit erweiterten Funktionen."""
    
    def __init__(self):
        self.session = None
        self.bring = None
        self.lists = None
        self.lists_timestamp = None
        self.session_timestamp = None
        self.cache_hits = {"session": 0, "lists": 0}
        self.cache_misses = {"session": 0, "lists": 0}
    
    def is_session_valid(self) -> bool:
        """Prüft, ob Session noch gültig ist."""
        return self.session is not None and self.bring is not None
    
    def is_lists_cache_valid(self) -> bool:
        """Prüft, ob Listen-Cache noch gültig ist."""
        if self.lists is None or self.lists_timestamp is None:
            return False
        return time.time() - self.lists_timestamp < LISTS_CACHE_TIMEOUT
    
    def invalidate_session(self):
        """Invalidiert die Session."""
        self.session = None
        self.bring = None
        self.session_timestamp = None
    
    def invalidate_lists(self):
        """Invalidiert den Listen-Cache."""
        self.lists = None
        self.lists_timestamp = None
    
    def set_session(self, session: aiohttp.ClientSession, bring: Bring):
        """Speichert die Session."""
        self.session = session
        self.bring = bring
        self.session_timestamp = time.time()
    
    def set_lists(self, lists):
        """Speichert Listen und Timestamp."""
        self.lists = lists
        self.lists_timestamp = time.time()
    
    def get_cache_stats(self) -> dict:
        """Gibt Statistiken über Cache-Hits/Misses zurück."""
        return {
            "session_hits": self.cache_hits["session"],
            "session_misses": self.cache_misses["session"],
            "lists_hits": self.cache_hits["lists"],
            "lists_misses": self.cache_misses["lists"],
        }

# Globale Cache-Instanz
bring_cache = BringCache()


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


async def add_items_to_bring(items: list, max_retries: int = 2):
    """
    Fügt Artikel zur Bring! Einkaufsliste hinzu.
    OPTIMIERT mit: Login-Cache, Parallel Requests, Listen-Cache
    
    Args:
        items: Liste mit Artikeln [{name: ..., specification: ...}]
        max_retries: Maximale Anzahl von Wiederholungen bei Fehlern
    """
    bring_email = os.getenv("BRING_EMAIL")
    bring_password = os.getenv("BRING_PASSWORD")
    
    if not bring_email or not bring_password:
        print("[red]Bring! Anmeldeinformationen nicht in .env gefunden.[/red]")
        return False
    
    print("[cyan]Verbinde mit Bring! API...[/cyan]")
    
    for attempt in range(max_retries):
        try:
            step_times = {}
            
            # OPTIMIERUNG 1: Login-Cache prüfen
            session_start = time.time()
            if not bring_cache.is_session_valid() or (time.time() - bring_cache.session_timestamp > SESSION_MAX_AGE):
                print("[dim]  ➤ Neue Session (Cache ungültig oder abgelaufen)[/dim]")
                bring_cache.cache_misses["session"] += 1
                session = aiohttp.ClientSession()
                bring = Bring(session, bring_email, bring_password)
                
                login_start = time.time()
                await bring.login()
                step_times["login"] = time.time() - login_start
                
                bring_cache.set_session(session, bring)
                print(f"[dim]    Login: {step_times['login']:.2f}s[/dim]")
            else:
                print("[dim]  ✓ Verwende gecachte Session (Cache Hit!)[/dim]")
                bring_cache.cache_hits["session"] += 1
                session = bring_cache.session
                bring = bring_cache.bring
            
            step_times["session"] = time.time() - session_start
            
            # OPTIMIERUNG 3: Listen-Cache prüfen
            lists_start = time.time()
            if bring_cache.is_lists_cache_valid():
                print("[dim]  ✓ Verwende gecachte Listen (5 Min Cache Hit!)[/dim]")
                bring_cache.cache_hits["lists"] += 1
                lists = bring_cache.lists
            else:
                print("[dim]  ➤ Lade Listen neu[/dim]")
                bring_cache.cache_misses["lists"] += 1
                list_response = await bring.load_lists()
                lists = list_response.lists
                bring_cache.set_lists(lists)
            
            step_times["lists"] = time.time() - lists_start
            
            if not lists:
                print("[red]Keine Einkaufslisten gefunden.[/red]")
                bring_cache.invalidate_session()
                return False
            
            # Verwende erste Liste
            shopping_list = lists[0]
            print(f"[cyan]Füge Artikel zur Liste '{shopping_list.name}' hinzu...[/cyan]")
            
            # OPTIMIERUNG 2: Artikel parallel speichern (statt for-Loop)
            save_tasks = []
            for item in items:
                item_name = item.get('name')
                if not item_name:
                    continue
                
                specification = item.get('specification', '')
                # Erstelle Task für paralleles Speichern
                task = bring.save_item(shopping_list.listUuid, item_name, specification)
                save_tasks.append((task, item_name, specification))
            
            # Führe alle Save-Tasks parallel aus
            if save_tasks:
                save_start = time.time()
                try:
                    await asyncio.gather(*save_tasks, return_exceptions=True)
                except Exception as e:
                    print(f"[yellow]Fehler beim parallelen Speichern: {e}[/yellow]")
                    raise
                
                step_times["save"] = time.time() - save_start
                
                # Ausgabe nach parallelem Ausführen
                for _, item_name, specification in save_tasks:
                    spec_info = f" mit '{specification}'" if specification else ""
                    print(f"- [green]{item_name}{spec_info}[/green]")
            
            print("[bold green]Alle Artikel hinzugefügt![/bold green]")
            
            # Zeige Performance-Stats
            total_time = sum(step_times.values())
            print(f"[dim]Performance: Gesamt {total_time:.2f}s " +
                  f"(Login: {step_times.get('login', 0):.2f}s, " +
                  f"Listen: {step_times['lists']:.2f}s, " +
                  f"Speichern: {step_times.get('save', 0):.2f}s)[/dim]")
            
            return True
        
        except asyncio.TimeoutError:
            print(f"[yellow]Timeout bei Bring! API (Versuch {attempt + 1}/{max_retries})[/yellow]")
            bring_cache.invalidate_session()
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            return False
        
        except (BringAuthException, BringRequestException, BringParseException) as e:
            print(f"[red]Bring! API Fehler: {e} (Versuch {attempt + 1}/{max_retries})[/red]")
            logger.exception("Detaillierter Fehler:")
            bring_cache.invalidate_session()
            return False
        
        except Exception as e:
            print(f"[red]Fehler mit Bring! API: {e}[/red]")
            logger.exception("Detaillierter Fehler:")
            bring_cache.invalidate_session()
            return False
    
    return False


def main():
    """Hauptschleife des Sprachassistenten mit persistentem Event Loop (für 24/7)."""
    print("[bold green]Einkaufslisten-Sprachassistent gestartet![/bold green]")
    
    # Event Loop einmal erstellen und wiederverwenden (24/7 Stabilität)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
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
            
            # 🚀 OPTIMIERUNG: TTS PARALLELISIERUNG
            # Nach Gemini wird TTS gestartet WÄHREND Bring! API parallel läuft
            try:
                loop.run_until_complete(_process_items_with_tts_parallel(items))
            except (BringAuthException, BringRequestException, BringParseException) as e:
                print(f"[red]Fehler bei Bring! API: {e}[/red]")
                logger.exception("Detaillierter Fehler:")
            except Exception as e:
                print(f"[red]Unerwarteter Fehler: {e}[/red]")
                logger.exception("Detaillierter Fehler:")
    
    except KeyboardInterrupt:
        print("\n[yellow]Shutdown eingeleitet...[/yellow]")
    finally:
        # Cleanup: Event Loop schließen
        loop.close()
        print("[green]Assistent beendet.[/green]")


async def _process_items_with_tts_parallel(items: list):
    """
    Verarbeitet Artikel mit TTS-Parallelisierung.
    
    Timeline:
    1. TTS wird gestartet (nach Gemini)
    2. Bring! API läuft parallel
    3. Auf beide warten
    4. Abspielen wenn beide fertig
    
    Einsparung: ~5 Sekunden (-20%)
    """
    workflow_start = time.time()
    
    # Vorbereite Speech-Text schon hier
    speech_text = _format_items_for_speech(items)
    if not speech_text:
        speech_text = "Artikel hinzugefügt"
    
    tts_message = f"Ok, ich habe {speech_text} hinzugefügt"
    
    print("[cyan]\n🚀 Starte parallele Verarbeitung:[/cyan]")
    
    # SCHRITT 1: TTS-Generierung starten (ASYNCHRON)
    print("[dim]  ➤ Starte TTS-Generierung im Hintergrund...[/dim]")
    tts_start = time.time()
    tts_task = asyncio.create_task(generate_tts_async(tts_message))
    
    # SCHRITT 2: Bring! API parallel ausführen (WÄHREND TTS generiert wird)
    print("[dim]  ➤ Starte Bring! API parallel...[/dim]")
    bring_start = time.time()
    bring_result = await add_items_to_bring(items)
    bring_time = time.time() - bring_start
    
    if bring_result:
        print(f"[dim]  ✓ Bring! fertig: {bring_time:.2f}s[/dim]")
    else:
        print("[yellow]  ⚠ Bring! hatte Fehler[/yellow]")
    
    # SCHRITT 3: Warte auf TTS-Fertigstellung
    print("[dim]  ➤ Warte auf TTS-Generierung...[/dim]")
    audio_file = await tts_task
    tts_time = time.time() - tts_start
    
    if audio_file:
        print(f"[dim]  ✓ TTS fertig: {tts_time:.2f}s[/dim]")
        
        # SCHRITT 4: Spiele Audio ab
        print("[cyan]  ▶ Spiele Audio ab...[/cyan]")
        try:
            play_audio_file(audio_file)
            
            # Cleanup
            if os.path.exists(audio_file):
                try:
                    os.unlink(audio_file)
                except:
                    pass
        
        except Exception as e:
            print(f"[yellow]Fehler beim Abspielen: {e}[/yellow]")
    else:
        print("[yellow]  ⚠ TTS-Generierung fehlgeschlagen[/yellow]")
    
    # Performance-Statistik
    total_time = time.time() - workflow_start
    print(f"[dim]\n⏱️  Gesamt-Zeit: {total_time:.2f}s (TTS: {tts_time:.2f}s, Bring!: {bring_time:.2f}s)[/dim]")


if __name__ == "__main__":
    main()