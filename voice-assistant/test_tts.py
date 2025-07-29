#!/usr/bin/env python3
"""
Test-Skript für das TTS-System
Testet verschiedene Szenarien der Sprachsynthese
"""

import sys
import os
import time

# Füge den src-Ordner zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tts import speak

def test_basic_tts():
    """Test der grundlegenden TTS-Funktionalität"""
    print("=== Test 1: Grundlegende TTS-Funktionalität ===")
    test_text = "Hallo, dies ist ein Test der Sprachsynthese."
    print(f"Teste Text: '{test_text}'")
    speak(test_text)
    print("Test 1 abgeschlossen.\n")

def test_empty_text():
    """Test mit leerem Text"""
    print("=== Test 2: Leerer Text ===")
    print("Teste leeren Text...")
    speak("")
    print("Test 2 abgeschlossen.\n")

def test_long_text():
    """Test mit längerem Text"""
    print("=== Test 3: Längerer Text ===")
    long_text = ("Dies ist ein längerer Text, um zu testen, "
                 "ob die Sprachsynthese auch mit komplexeren "
                 "und längeren Sätzen funktioniert. "
                 "Das System sollte diesen Text vollständig "
                 "und verständlich wiedergeben können.")
    print(f"Teste langen Text: '{long_text[:50]}...'")
    speak(long_text)
    print("Test 3 abgeschlossen.\n")

def test_special_characters():
    """Test mit Sonderzeichen und Zahlen"""
    print("=== Test 4: Sonderzeichen und Zahlen ===")
    special_text = "Die Temperatur beträgt 23,5 Grad Celsius. Das sind etwa 74°F!"
    print(f"Teste Text mit Sonderzeichen: '{special_text}'")
    speak(special_text)
    print("Test 4 abgeschlossen.\n")

def test_multiple_sentences():
    """Test mit mehreren Sätzen"""
    print("=== Test 5: Mehrere Sätze ===")
    multi_text = ("Erster Satz. Zweiter Satz mit mehr Inhalt. "
                  "Dritter Satz zum Abschluss des Tests.")
    print(f"Teste mehrere Sätze: '{multi_text}'")
    speak(multi_text)
    print("Test 5 abgeschlossen.\n")

def interactive_test():
    """Interaktiver Test - Benutzer kann eigenen Text eingeben"""
    print("=== Interaktiver Test ===")
    print("Geben Sie Text ein, der gesprochen werden soll (Enter für Beenden):")
    
    while True:
        user_input = input("> ").strip()
        if not user_input:
            break
        speak(user_input)
    
    print("Interaktiver Test beendet.\n")

def main():
    """Hauptfunktion - führt alle Tests aus"""
    print("TTS Test-Suite gestartet")
    print("=" * 50)
    
    try:
        # Automatische Tests
        test_basic_tts()
        time.sleep(1)
        
        test_empty_text()
        time.sleep(1)
        
        test_long_text()
        time.sleep(1)
        
        test_special_characters()
        time.sleep(1)
        
        test_multiple_sentences()
        time.sleep(1)
        
        # Interaktiver Test (optional)
        print("Möchten Sie den interaktiven Test durchführen? (j/n): ", end="")
        if input().lower().startswith('j'):
            interactive_test()
        
        print("=" * 50)
        print("Alle Tests abgeschlossen!")
        
    except KeyboardInterrupt:
        print("\nTests durch Benutzer abgebrochen.")
    except Exception as e:
        print(f"Fehler während der Tests: {e}")

if __name__ == "__main__":
    main()
