import os
import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

class EmbeddingsService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_text(self, text: str) -> list[float]:
        return self.model.encode(text)
