from ollama import Client
import os

class EmbeddingsService:
    def __init__(self, model="qwen3-embedding:0.6b"):
        self.client = Client(host="http://localhost:11434")
        self.model = model

    def embed_text(self, text: str):
        response = self.client.embeddings(
            model=self.model,
            prompt=text
        )
        return response["embedding"]
