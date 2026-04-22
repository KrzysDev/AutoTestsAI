import httpx
import os
import dotenv
from ollama import Client

dotenv.load_dotenv()

class AiService:
    def __init__(self):
        self.ollama_client = Client(
            host="https://ollama.com",
            headers={'Authorization': 'Bearer ' + str(os.getenv('OLLAMA_API_KEY'))}
        )
        self.model = "gemini-3-flash-preview"

    def ask(self, text: str):
        is_testing = os.getenv("AI_TESTING", "false").lower() == "true"

        if is_testing:
            response = self.ollama_client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            )
            return response["message"]["content"]
        else:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": text
                            }
                        ]
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]