import os
from ollama import Client
from dotenv import load_dotenv

load_dotenv()

class AiService:
    def __init__(self):
        api_key = os.environ.get('OLLAMA_API_KEY')
        if not api_key:
            raise RuntimeError("brak klucza API")
            
        self.cloud_client = Client(
            host="https://ollama.com",
            headers={'Authorization': f'Bearer {api_key}'}
        )

        self.local_client = Client(
            host="http://localhost:11434"
        )

    def ask_local(self, text: str):
        response = self.local_client.chat(model='qwen3.5', messages=[
        {
            'role': 'user',
            'content': text,
        },
        ])
        return {"message": response['message']['content']}

    def ask_local_with_photo(self, text:str, photo_path:str):
        with open(photo_path, 'rb') as f:
            photo_bytes = f.read()

        response = self.local_client.chat(
        model='qwen3.5',
        messages=[
            {
            'role': 'user',
            'content': text,
            'images': [photo_bytes],
            }
        ],
        )
        return {"message": response['message']['content']}

    def ask_cloud(self, text: str):
        message = [{
            'role' : 'user',
            'content': text
        },
        ]

        parts = []
        for part in self.cloud_client.chat('gpt-oss:120b', messages=message, stream=True):
            parts.append(part['message']['content'])
        return {"message": "".join(parts)}