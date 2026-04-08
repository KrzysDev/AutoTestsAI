import os
import requests
from dotenv import load_dotenv
import ollama
from sentence_transformers import SentenceTransformer
import logging

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

load_dotenv()

class EmbeddingsService:
    def __init__(self):
        self.model = SentenceTransformer("intfloat/multilingual-e5-large")

    def embed_text(self, text: str) -> list[float]:
        response = self.model.encode(
            text,
        )
        return response
