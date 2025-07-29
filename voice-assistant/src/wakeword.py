import os
import pvporcupine
from pvrecorder import PvRecorder


def listen_for_wakeword():
    access_key = os.getenv("PICOVOICE_ACCESS_KEY")
    if not access_key:
        raise RuntimeError("PICOVOICE_ACCESS_KEY nicht gesetzt. Bitte in .env eintragen.")
    porcupine = pvporcupine.create(access_key=access_key, keywords=["alexa"])
    recorder = PvRecorder(device_index=1, frame_length=porcupine.frame_length)
    print("[Wakeword-Modul] Warte auf Wakeword 'alexa'...")
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