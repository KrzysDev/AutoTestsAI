import os
from ollama import Client
from dotenv import load_dotenv

load_dotenv()

class AiService:
    def __init__(self):
        api_key = os.environ.get('OLLAMA_API_KEY')
        if not api_key:
            raise RuntimeError("Zmienna środowiskowa OLLAMA_API_KEY jest wymagana, ale jej brakuje!")
            
        self.client = Client(
            host="https://ollama.com",
            headers={'Authorization': f'Bearer {api_key}'}
        )

    def ask_local(self, text: str):
        response = self.client.chat(model='qwen3-coder:30b', messages=[
        {
            'role': 'user',
            'content': text,
        },
        ])
        return {"message": response['message']['content']}

    def ask_cloud(self, text: str):
        message = [{
            'role' : 'user',
            'content': text
        },
        ]

        parts = []
        for part in self.client.chat('gpt-oss:120b', messages=message, stream=True):
            parts.append(part['message']['content'])
        return {"message": "".join(parts)}