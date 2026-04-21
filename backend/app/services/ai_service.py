import requests
import os
import dotenv

dotenv.load_dotenv()

class AiService:
    def __init__(self):
        pass

    def ask(self, text: str):
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            },
            json={
                "model": "google/gemini-3.1-flash-lite-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            }
        )

        data = response.json()
        return data["choices"][0]["message"]["content"]