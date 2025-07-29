import os
import requests
import json

def extract_shopping_list_from_audio(audio_bytes):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY nicht gesetzt. Bitte in .env eintragen.")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    prompt = (
        "Extrahiere die Einkaufsliste aus dem folgenden Audio. Gib das Ergebnis als JSON-Array zurück. "
        "Jedes Element im Array sollte ein Objekt mit den Schlüsseln 'name' und 'specification' sein. "
        "'name' ist der Produktname (z.B. 'Eier'), 'specification' ist die Mengenangabe (z.B. '2 Stück' oder '1kg'). "
        "Schreibe Zahlen immer als Zahlen und nicht als Text. Beispiel: '2 Eier' statt 'zwei Eier'. "
        "Wenn keine Mengenangabe vorhanden ist, lasse 'specification' als leeren String. "
        "Wenn keine Produkte genannt werden oder das Audio nur Stille enthält, gib ein leeres JSON-Array '[]' zurück."
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
    try:
        # Die Antwort könnte in einem Markdown-Codeblock sein, z.B. ```json ... ```
        if '```json' in output:
            output = output.split('```json')[1].split('```')[0].strip()
        elif output.startswith('```') and output.endswith('```'):
            output = output[3:-3].strip()

        parsed_list = json.loads(output)

        if not isinstance(parsed_list, list):
            print(f"[Warnung] Gemini-Antwort ist kein JSON-Array: {parsed_list}")
            return []

        # Überprüfe die Struktur jedes Elements
        for item in parsed_list:
            if not isinstance(item, dict) or 'name' not in item:
                print(f"[Warnung] Ungültiges Element in der Liste: {item}")
                return []  # Ungültige Liste verwerfen
            # Stelle sicher, dass 'specification' immer existiert
            if 'specification' not in item:
                item['specification'] = ""

        return parsed_list

    except (json.JSONDecodeError, TypeError) as e:
        print(f"[Fehler] JSON-Antwort von Gemini konnte nicht verarbeitet werden: {e}")
        print(f"[Debug] Rohe Antwort: {output}")
        return []