import os
from ollama import Client
from dotenv import load_dotenv

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

        self.local_client = Client(
            host="http://localhost:11434",
        )

    def ask_ollama_local(self, text: str):
        response = self.local_client.chat(model='qwen3.5', messages=[
            {
                'role': 'user',
                'content': text,
            },
        ])
        return {"message": response['message']['content']}

    def ask_ollama_local_with_photo(self, text: str, photo_path: str):
        with open(photo_path, "rb") as f:
            photo_data = f.read()

        response = self.local_client.chat(
            model='qwen2.5vl:7b',
            messages=[
                {
                    'role': 'user',
                    'content': text,
                    'images': [photo_data],
                }
            ],
            options={
                "temperature": 0,
                "num_predict": 4096,
                "num_ctx": 8192
            }
        )
        return {"message": response['message']['content']}

    def ask_ollama_cloud(self, text: str):
        message = [
            {
                'role': 'user',
                'content': text
            },
        ]

        parts = []
        for part in self.cloud_client.chat('qwen3-vl:235b-cloud', messages=message, stream=True):
            parts.append(part['message']['content'])
        return {"message": "".join(parts)}
    
    def ask_ollama_cloud_with_photo(self, text: str, photo_path: str):
        with open(photo_path, "rb") as f:
            photo_data = f.read()

        message = [
            {
                'role': 'user',
                'content': text,
                'images': [photo_data],
            },
        ]

        parts = []
        for part in self.cloud_client.chat('qwen3-vl:235b-cloud', messages=message, stream=True):
            parts.append(part['message']['content'])
        return "".join(parts)