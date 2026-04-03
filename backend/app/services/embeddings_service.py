import os
import requests
from dotenv import load_dotenv
import ollama

load_dotenv()

class EmbeddingsService:
    def __init__(self):
        self.client = ollama.Client(
            host="http://localhost:11434",
        )

    def embed_text(self, text: str) -> list[float]:
        response = ollama.embed(
            model='qwen3-embedding:0.6b',
            input=text,
        )
        return response.embeddings[0]
