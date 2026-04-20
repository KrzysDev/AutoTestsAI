import os
from ollama import Client
from dotenv import load_dotenv
import json
from backend.app.models.prompts import SystemPrompts

import os

import time

load_dotenv()

# Service for interacting with LLM APIs (Ollama), handling both local and cloud inference.
# Provides text and document analysis capabilities.
# </summary>
class AiService:
    def __init__(self):
        # Ollama configuration
        ollama_api_key = os.environ.get('OLLAMA_API_KEY')
        
        if not ollama_api_key:
            print("Warning: No OLLAMA API key found")
            
        self.cloud_client = Client(
            host="https://ollama.com",
            headers={'Authorization': f'Bearer {ollama_api_key}'} if ollama_api_key else {}
        )

        self.prompts = SystemPrompts()

        self.local_client = Client(
            host="http://localhost:11434",
        )

    def ask(self, text: str):
        if os.environ.get('AI_CLOUD_MODE').lower() == 'true':
            return self.__ask_ollama_cloud(text, 'gemma4:31b-cloud')
        else:
            return self.__ask_ollama_local(text, model="gemma4:latest")         

    def ask_model(self, text: str, model: str):
        if os.environ.get('AI_CLOUD_MODE').lower() == 'true':
            return self.__ask_ollama_cloud(text, model)
        else:
            return self.__ask_ollama_local(text, model) 


    # --- Legacy / Internal Methods ---

    def __ask_ollama_local(self, text: str, model: str):
        response = self.local_client.chat(model=model, messages=[
            {
                'role': 'user',
                'content': text,
            },
        ])
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
                print(f"Attempt {attempt + 1}/{retries} failed: {e}")

                if attempt < retries - 1:
                    print(f"Waiting {wait}s before next attempt...")
                    time.sleep(wait)

        return "Error: Could not connect to Ollama"
