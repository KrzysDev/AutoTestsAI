import httpx
import os
import dotenv
from ollama import Client
from openrouter import OpenRouter

dotenv.load_dotenv(dotenv.find_dotenv(), override=True)

class AiService:
    def __init__(self):
        self.ollama_client = Client(
            host="https://ollama.com",
            headers={'Authorization': 'Bearer ' + str(os.getenv('OLLAMA_API_KEY'))}
        )
        self.local_ollama_client = Client(
            host="http://localhost:11434"
        )

    def ask(self, text: str, model: str):
        is_testing = os.getenv("AI_TESTING", "false").lower() == "true"

        if is_testing:
            response = self.ollama_client.chat(
                #diffrent model is used for testing
                model="gemma4:31b-cloud",
                messages=[
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            )
            return response["message"]["content"]
        else:
            with OpenRouter(
                api_key=os.getenv("OPENROUTER_API_KEY", ""),
                ) as client:
                response = client.chat.send(
                    model="openai/gpt-5-mini",
                    messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{text}"
                            },
                        ]
                    }
                    ]
                )

                return response.choices[0].message.content

    def ask_local(self, text: str):
        response = self.local_ollama_client.chat(
            model="qwen2.5:14b-instruct",
            messages=[
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        return response["message"]["content"]