import os
from ollama import Client
from google import genai
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
            self.gemini_client = genai.Client(api_key=gemini_api_key)
        else:
            print("Warning: No GOOGLE_API_KEY found. Gemini functions will fail.")
            self.gemini_client = None

    def ask(self, text: str):
        """
        Unified method to submit a prompt to the primary AI engine (Gemini 1.5 Flash).
        """
        return self.ask_gemini(text)

    def ask_gemini(self, text: str):
        """
        Submits a prompt to Google Gemini 1.5 Flash for high-speed inference.
        """
        if not self.gemini_client:
            raise RuntimeError("Gemini is not configured. Please add GOOGLE_API_KEY to .env")
            
        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=text
            )
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            raise RuntimeError(f"Failed to get response from Gemini: {e}")

    def ask_gemini_with_photo(self, text: str, photo_path: str):
        """
        Submits a prompt with an image to Google Gemini 1.5 Flash (Vision).
        """
        if not self.gemini_client:
            raise RuntimeError("Gemini is not configured. Please add GOOGLE_API_KEY to .env")
            
        try:
            with open(photo_path, "rb") as f:
                image_data = f.read()
            
            # Gemini SDK handles raw bytes directly in contents list if specified correctly
            # Or we can use types.Part.from_bytes if we had imported it
            from google.genai import types
            response = self.gemini_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=[
                    types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                    text
                ]
            )
            return response.text
        except Exception as e:
            print(f"Error calling Gemini Vision: {e}")
            raise RuntimeError(f"Failed to get vision response from Gemini: {e}")

    def __classify_text(self, text: str):
        """
        Classifies user prompt using Gemini.
        """
        prompt = self.prompts.get_classification_prompt(text)
        response_text = self.ask_gemini(prompt)
        
        # We assume classification logic handles the string response
        return response_text

    # --- Legacy / Internal Methods ---

    def __ask_ollama_local(self, text: str, model: str):
        response = self.local_client.chat(model=model, messages=[
            {
                'role': 'user',
                'content': text,
            },
        ])
        return response['message']['content']

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