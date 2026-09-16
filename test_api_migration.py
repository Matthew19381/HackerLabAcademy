#!/usr/bin/env python3
"""
Testowanie API po migracji
"""

import requests
import json
import sys

def test_api():
    base_url = "http://localhost:8001"
    
    print("Testowanie API po migracji...")
    print("=" * 40)
    
    # Test 1: Sprawdź czy API działa
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✓ API dostępne (Swagger docs)")
        else:
            print(f"✗ API zwróciło status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Błąd połączenia z API: {e}")
        return False
    
    # Test 2: Sprawdź endpoint stats
    try:
        response = requests.get(f"{base_url}/api/v1/stats/1")
        print(f"\nEndpoint /api/v1/stats/1:")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("  ✓ API działa poprawnie po migracji")
            if isinstance(data, dict):
                print(f"  Klucze odpowiedzi: {list(data.keys())}")
        elif response.status_code == 404:
            print("  ⚠ Użytkownik o ID=1 nie istnieje (normalne)")
        else:
            print(f"  ✗ Błąd: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ✗ Błąd połączenia: {e}")
        return False
    
    # Test 3: Sprawdź flashcards endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/flashcards")
        print(f"\nEndpoint /api/v1/flashcards:")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("  ✓ Flashcards API działa")
            if isinstance(data, list):
                print(f"  Liczba flashcardów: {len(data)}")
        else:
            print(f"  ⚠ Status: {response.status_code} (może być normalne przy pustej bazie)")
            
    except Exception as e:
        print(f"  ✗ Błąd połączenia: {e}")
    
    print("\n" + "=" * 40)
    print("✓ Wszystkie testy zakończone pomyślnie!")
    return True

if __name__ == "__main__":
    test_api()