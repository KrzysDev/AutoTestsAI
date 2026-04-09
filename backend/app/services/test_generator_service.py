from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.models.prompts import SystemPrompts
from backend.app.models.schemas import (
    Test, Question, RetrivedChunk,
    Chunk, ChunkMetadata, GeneratedTestSection
)
from backend.app.services.embeddings_service import EmbeddingsService
import json
import ast


class TestGeneratorService:
    def __init__(self):
        self.ai_service = AiService()
        self.search_service = SearchService()
        self.prompts = SystemPrompts()
        self.embeddings_service = EmbeddingsService()

    def generate_test(self, topic: str):
        pass