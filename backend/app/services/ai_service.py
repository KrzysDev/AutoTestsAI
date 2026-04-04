import os
from ollama import Client
from dotenv import load_dotenv
import json
from app.models.prompts import SystemPrompts
from app.models.schemas import TeacherRequestClassification, Question

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

    def ask_ollama_local(self, text: str, model: str):
        response = self.local_client.chat(model=model, messages=[
            {
                'role': 'user',
                'content': text,
            },
        ])
        return response['message']['content']

    def classify_text(self, text: str):
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

    def ask_ollama_local_with_photo(self, text: str, photo_path: str):
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

    def ask_ollama_cloud(self, text: str, model: str):
        message = [
            {
                'role': 'user',
                'content': text
            },
        ]

        parts = []
        try:
            for part in self.cloud_client.chat(model, messages=message, stream=True):
                parts.append(part['message']['content'])
        except Exception as e:
            print(e)
            return "Error: Could not connect to Ollama"
        return "".join(parts)
    
    def ask_ollama_cloud_with_photo(self, text: str, photo_path: str, model: str):
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