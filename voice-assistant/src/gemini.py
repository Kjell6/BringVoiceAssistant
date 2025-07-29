import os
import requests

def extract_shopping_list_from_audio(audio_bytes):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY nicht gesetzt. Bitte in .env eintragen.")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    prompt = (
        "Extrahiere die Einkaufsliste aus folgendem Audio. Gib nur die Liste der Produkte als Komma-separierte Zeichenkette zurück."
    )
    # Audio als base64-codierten String einbetten
    import base64
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    data = {
        "contents": [
            {"parts": [
                {"text": prompt},
                {"inline_data": {
                    "mime_type": "audio/wav",
                    "data": audio_b64
                }}
            ]}
        ],
        "generationConfig": {"temperature": 0.2}
    }
    params = {"key": api_key}
    try:
        response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.HTTPError as e:
        print(f"[red]Fehler bei der Anfrage an die Gemini API: {e}[/red]")
        # Versuche, mehr Details aus der Antwort zu bekommen, falls vorhanden
        try:
            error_details = e.response.json()
            print(f"[red]API-Fehlerdetails: {error_details.get('error', {}).get('message', 'Keine Details')}[/red]")
        except (ValueError, AttributeError):
            print(f"[red]Keine weiteren Fehlerdetails in der API-Antwort.[/red]")
        return []
    try:
        candidate = result["candidates"][0]["content"]
        # Falls 'candidate' kein dict ist oder keine sinnvollen Felder enthält, leere Liste zurückgeben
        if not isinstance(candidate, dict):
            print("[Warnung] Unerwartetes Antwortformat von Gemini:", result)
            print("[Debug] Komplette Gemini-Antwort:", result)
            return []
        # Versuche zuerst, das 'parts'-Feld zu lesen
        parts = candidate.get("parts")
        if parts and isinstance(parts, list) and "text" in parts[0]:
            output = parts[0]["text"]
        # Falls nicht vorhanden, prüfe auf direktes 'text'-Feld
        elif "text" in candidate:
            output = candidate["text"]
        else:
            # Wenn keine sinnvollen Felder vorhanden sind, leere Liste zurückgeben
            print("[Warnung] Keine Produkte extrahiert. Antwort von Gemini:", result)
            print("[Debug] Komplette Gemini-Antwort:", result)
            return []
    except (KeyError, IndexError):
        print("[Fehler] Antwort von Gemini konnte nicht gelesen werden:", result)
        print("[Debug] Komplette Gemini-Antwort:", result)
        return []
    return [item.strip() for item in output.split(",") if item.strip()] 