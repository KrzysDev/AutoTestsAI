import urllib.request
import json

URL = "http://localhost:8000/v1/rag/test/generate/by_survey"

# Przykładowe payload bazujące na TestSurveyRequest -> Form -> FormSection
payload = {
    "form": {
        "level": "B2",
        "age_group": "adults",
        "sections": [
            {
                "task_type": "grammar",
                "subject": "Present Perfect vs Past Simple",
                "amount": 2,
                "additional_comment": "Focus on the differences in usage."
            },
            {
                "task_type": "reading",
                "subject": "reading",
                "amount": 1,
                "additional_comment": "Keep the text engaging, maybe about travel."
            }
        ],
        "total_amount": 3,
        "additional_notes": "Make the test quite advanced but clear."
    }
}

def test_survey_generation():
    print(f"Wysyłam zapytanie do: {URL}")
    print(f"Payload:\n{json.dumps(payload, indent=2)}")
    
    req = urllib.request.Request(URL, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            print("\nSukces! Otrzymano odpowiedź 200 OK.")
            data = json.loads(response.read().decode('utf-8'))
            
            # Pokażmy tylko metadata i fragment testu
            metadata = data.get("metadata", {})
            print("\n[Metadane]:")
            print(json.dumps(metadata, indent=2))
            
            test_response = data.get("response", {})
            exercises = test_response.get("exercises", [])
            print(f"\n[Wygenerowano ćwiczeń]: {len(exercises)}")
            
            for i, ex in enumerate(exercises):
                print(f"\n--- Ćwiczenie {i+1} ---")
                print(f"Instrukcja: {ex.get('instruction')}")
                # Fragment treści ćwiczenia
                body = ex.get('body', "")
                print(f"Body (pierwsze 100 znaków): {body[:100]}...")
            
    except urllib.error.HTTPError as e:
        print(f"\nBłąd! Kod statusu: {e.code}")
        print("Odpowiedź:")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"\nBłąd! Kod statusu: Nieznany ({e})")

if __name__ == "__main__":
    test_survey_generation()
