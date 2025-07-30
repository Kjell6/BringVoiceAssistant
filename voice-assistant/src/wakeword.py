import os
import pvporcupine
from pvrecorder import PvRecorder


def listen_for_wakeword():
    access_key = os.getenv("PICOVOICE_ACCESS_KEY")
    if not access_key:
        raise RuntimeError("PICOVOICE_ACCESS_KEY nicht gesetzt. Bitte in .env eintragen.")
    
    # Prüfe ob Custom Wakeword-Dateien vorhanden sind
    current_dir = os.path.dirname(os.path.abspath(__file__))
    custom_keyword_path = os.path.join(current_dir, 'heyListe.ppn')
    custom_model_path = os.path.join(current_dir, 'PorcupineDe.pv')
    
    # Verwende Custom Wakeword falls vorhanden, sonst vorgefertigtes Wakeword
    if os.path.exists(custom_keyword_path) and os.path.exists(custom_model_path):
        # Custom Wakeword verwenden
        keyword_path = os.getenv("WAKEWORD_KEYWORD_PATH", custom_keyword_path)
        model_path = os.getenv("WAKEWORD_MODEL_PATH", custom_model_path)
        wakeword_name = os.getenv("WAKEWORD_NAME", "heyListe")
        print(f"[Wakeword-Modul] Verwende Custom Wakeword '{wakeword_name}'...")
        
        # Prüfe ob die Dateien existieren
        if not os.path.exists(keyword_path):
            raise RuntimeError(f"Wakeword-Datei nicht gefunden: {keyword_path}")
        if not os.path.exists(model_path):
            raise RuntimeError(f"Sprachmodell-Datei nicht gefunden: {model_path}")
        
        porcupine = pvporcupine.create(access_key=access_key, keyword_paths=[keyword_path], model_path=model_path)
    else:
        # Vorgefertigtes Wakeword verwenden
        wakeword_name = os.getenv("WAKEWORD_NAME", "Alexa")
        wakeword_keyword = os.getenv("WAKEWORD_KEYWORD", "alexa")
        
        print(f"[Wakeword-Modul] Keine Custom Wakeword-Dateien gefunden. Verwende vorgefertigtes Wakeword '{wakeword_name}'.")
        print(f"[Wakeword-Modul] Hinweis: Für Custom Wakewords, lade die Dateien in das src/ Verzeichnis herunter.")
        print(f"[Wakeword-Modul] Oder setze WAKEWORD_KEYWORD in der .env für andere vorgefertigte Wakewords.")
        
        porcupine = pvporcupine.create(access_key=access_key, keywords=[wakeword_keyword])
    
    recorder = PvRecorder(device_index=1, frame_length=porcupine.frame_length)
    
    print(f"[Wakeword-Modul] Warte auf Wakeword '{wakeword_name}'...")
    
    try:
        recorder.start()
        while True:
            pcm = recorder.read()
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("[Wakeword-Modul] Wakeword erkannt!")
                break
    finally:
        recorder.stop()
        recorder.delete()
        porcupine.delete() 