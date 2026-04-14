import os
from ollama import Client
import google.generativeai as genai
from dotenv import load_dotenv
import json
from backend.app.models.prompts import SystemPrompts


import time

load_dotenv()

# <summary>
# Service for interacting with LLM APIs (Ollama and Gemini), handling both local and cloud inference.
# Provides text and document analysis capabilities and classification utility methods.
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

        # Gemini configuration
        gemini_api_key = os.environ.get('GOOGLE_API_KEY')
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            print("Warning: No GOOGLE_API_KEY found. Gemini functions will fail.")
            self.gemini_model = None

    def ask(self, text: str):
        if os.environ.get('AI_CLOUD_MODE') == 'true':
            return self.__ask_ollama_cloud(text, 'gemma4:31b-cloud')
        else:
            return self.__ask_ollama_local(text, 'gemma3:4b')

    def ask_gemini(self, text: str):
        """
        Submits a prompt to Google Gemini 1.5 Flash for high-speed inference.
        """
        if not self.gemini_model:
            raise RuntimeError("Gemini is not configured. Please add GOOGLE_API_KEY to .env")
            
        try:
            response = self.gemini_model.generate_content(text)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            raise RuntimeError(f"Failed to get response from Gemini: {e}")

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
                print(f"Attempt {attempt + 1}/{retries} failed: {e}")

                if attempt < retries - 1:
                    print(f"Waiting {wait}s before next attempt...")
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