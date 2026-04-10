import requests
import json

def test_generation():
    url = "http://localhost:8000/v1/generator/generate"
    payload = {
        "language": "en",
        "level": "B2",
        "topic": "English Grammar - Present Simple",
        "group_count": 1
    }
    try:
        # We expect this might take a long time or fail if Ollama is not local
        # But we want to see if the router catches it.
        response = requests.post(url, json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.Timeout:
        print("Timeout (Expected if Ollama is slow)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_generation()
