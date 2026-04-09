import os
from ollama import Client
from dotenv import load_dotenv
import json
from backend.app.models.prompts import SystemPrompts
from backend.app.models.schemas import TeacherRequestClassification, Question

import time

load_dotenv()

class AiService:
    def __init__(self):
        api_key = os.environ.get('OLLAMA_API_KEY')
        
        if not api_key:
            raise RuntimeError("Error: No OLLAMA API key")
        self.cloud_client = Client(
            host="https://ollama.com",
            headers={'Authorization': f'Bearer {api_key}'}
        )

        self.prompts = SystemPrompts()

        self.local_client = Client(
            host="http://localhost:11434",
        )

    def ask(self, text: str):
        if os.environ.get('AI_CLOUD_MODE') == 'true':
            return self.__ask_ollama_cloud(text, 'gemma4:31b-cloud')
        else:
            return self.__ask_ollama_local(text, 'gemma3:4b')

    def __ask_ollama_local(self, text: str, model: str):
        response = self.local_client.chat(model=model, messages=[
            {
                'role': 'user',
                'content': text,
            },
        ])
        return response['message']['content']

    def __classify_text(self, text: str):
        message = [
            {
                'role': 'user',
                'content': self.prompts.get_classification_prompt(text)
            },
        ]

        response = self.cloud_client.chat('gemma3:4b-cloud', messages=message)
        classification = TeacherRequestClassification(
            text=text,
            classification=response['message']['content']
        )

        return classification.classification

    def __ask_ollama_local_with_photo(self, text: str, photo_path: str):
        with open(photo_path, "rb") as f:
            photo_data = f.read()

        response = self.local_client.chat(
            model='qwen3.5',
            messages=[
                {
                    'role': 'user',
                    'content': text,
                    'images': [photo_data],
                }
            ],
            stream=False
        )
        return response['message']['content']

    def __ask_ollama_cloud(self, text: str, model: str, retries=5):
        message = [
            {
                'role': 'user',
                'content': text
            },
        ]

        options = {
            "temperature": 0.0,
            "top_p": 1.0
        }

        for attempt in range(retries):
            parts = []
            try:
                for part in self.cloud_client.chat(
                    model,
                    messages=message,
                    stream=True,
                    options=options
                ):
                    parts.append(part['message']['content'])

                return "".join(parts)

            except Exception as e:
                wait = 2 ** attempt
                print(f"Próba {attempt + 1}/{retries} nieudana: {e}")

                if attempt < retries - 1:
                    print(f"Czekam {wait}s przed kolejną próbą...")
                    time.sleep(wait)

        return "Error: Could not connect to Ollama"
    
    def __ask_ollama_cloud_with_photo(self, text: str, photo_path: str, model: str):
        with open(photo_path, "rb") as f:
            photo_data = f.read()

        message = [
            {
                'role': 'user',
                'content': text,
                'images': [photo_data],
            },
        ]

        response = self.cloud_client.chat(model, messages=message)
        return response['message']['content']