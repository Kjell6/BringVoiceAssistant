import os
import json
import base64
import requests

# Konstanten
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
PROMPT = (
    "Extrahiere alle Produkte aus diesem Audio als JSON-Array. "
    "Format: [{\"name\": \"Produktname\", \"specification\": \"Menge/Details\"}]. "
    "Zahlen als Zahlen (nicht Text). Gewichte in kg/g. "
    "Specification leer lassen wenn nicht vorhanden. "
    "Bei Stille: leeres Array '[]'."
)


def _extract_json_from_response(text: str) -> str:
    """Extrahiert JSON aus Markdown-Codeblöcken falls vorhanden."""
    if '```json' in text:
        return text.split('```json')[1].split('```')[0].strip()
    elif text.startswith('```') and text.endswith('```'):
        return text[3:-3].strip()
    return text


def _validate_shopping_list(data: list) -> bool:
    """Validiert die Struktur der Einkaufsliste."""
    if not isinstance(data, list):
        return False
    
    for item in data:
        if not isinstance(item, dict) or 'name' not in item:
            return False
        # Stelle sicher, dass 'specification' existiert
        if 'specification' not in item:
            item['specification'] = ""
    
    return True


def extract_shopping_list_from_audio(audio_bytes: bytes) -> list:
    """
    Extrahiert Einkaufsliste aus Audio mittels Gemini API.
    
    Args:
        audio_bytes: WAV Audio-Daten als Bytes
    
    Returns:
        Dict mit: {"items": list, "error": str oder None}
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Fehler: GEMINI_API_KEY nicht in .env gesetzt")
        return {"items": [], "error": "GEMINI_API_KEY nicht konfiguriert"}
    
    # Bereite Request vor
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    payload = {
        "contents": [{
            "parts": [
                {"text": PROMPT},
                {"inline_data": {
                    "mime_type": "audio/wav",
                    "data": audio_b64
                }}
            ]
        }],
        "generationConfig": {"temperature": 0.2}
    }
    
    # API-Aufruf
    try:
        response = requests.post(
            GEMINI_API_URL,
            headers={"Content-Type": "application/json"},
            params={"key": api_key},
            json=payload,
            timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Fehler: Gemini API Timeout (30s)")
        return {"items": [], "error": "Gemini API Timeout"}
    except requests.exceptions.HTTPError as e:
        error_msg = "Fehler bei Gemini API"
        # Rate Limit Handling (429)
        if e.response.status_code == 429:
            error_msg = "Gemini API Rate Limit erreicht - bitte später versuchen"
            print(f"[yellow]{error_msg}[/yellow]")
            return {"items": [], "error": error_msg}
        try:
            error_msg += f": {e.response.json().get('error', {}).get('message', str(e))}"
        except Exception:
            error_msg += f": {e}"
        print(error_msg)
        return {"items": [], "error": error_msg}
    except Exception as e:
        print(f"Fehler bei Gemini API Aufruf: {e}")
        return {"items": [], "error": f"Gemini API Fehler: {e}"}
    
    # Parse Response
    try:
        result = response.json()
        candidate = result.get("candidates", [{}])[0].get("content", {})
        
        # Extrahiere Text aus parts oder direktem Feld
        text_output = None
        if "parts" in candidate and isinstance(candidate["parts"], list):
            text_output = candidate["parts"][0].get("text")
        else:
            text_output = candidate.get("text")
        
        if not text_output:
            print("Warnung: Keine Textantwort von Gemini erhalten")
            return {"items": [], "error": "Keine Textantwort von Gemini"}
        
        # Parse JSON
        json_text = _extract_json_from_response(text_output)
        shopping_list = json.loads(json_text)
        
        # Validiere Struktur
        if not _validate_shopping_list(shopping_list):
            print("Warnung: Ungültige Einkaufslisten-Struktur")
            return {"items": [], "error": None}  # Keine Fehler, nur ungültiges Format
        
        return {"items": shopping_list, "error": None}
    
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        print(f"Fehler beim Parse der Gemini-Antwort: {e}")
        return {"items": [], "error": None}  # Keine Fehler bei der API, nur Parse-Problem
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
        return {"items": [], "error": f"Unerwarteter Fehler: {e}"}