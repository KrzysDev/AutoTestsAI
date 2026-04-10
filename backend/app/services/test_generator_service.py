from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.models.prompts import SystemPrompts
from backend.app.services.embeddings_service import EmbeddingsService
import json
import ast
from typing import Literal
from backend.app.services.classification_service import ClassificationService
from backend.app.services.prompt_parser_service import PromptParserService
from backend.app.models.schemas import ParsedPrompt


# <summary>
# Service responsible for generating educational tests by orchestrating AI and search components.
# Includes classification, prompt parsing, retrieval, and final test generation.
# </summary>
class TestGeneratorService:
    def __init__(self):
        self.ai_service = AiService()
        self.search_service = SearchService()
        self.prompts = SystemPrompts()
        self.embeddings_service = EmbeddingsService()
        self.classification_service = ClassificationService()
        self.prompt_parser_service = PromptParserService()

    def generate_test(self, 
                      prompt: str, 
                      level: Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2'], 
                      age_group: Literal["kids", "teens", "adults"],
                      total_amount: int) -> str:
        """
        Generates a test based on the user prompt and configuration.
        """
        if self.classification_service.classify(prompt) == "normal":
            classified_prompt = self.prompt_parser_service.parse_prompt(prompt)
            json_classified_prompt = json.loads(classified_prompt)

            parsed_prompt = ParsedPrompt(
                task=prompt,
                level=level,
                age_group=age_group,
                sections=json_classified_prompt['sections'],
                total_amount=total_amount
            )

            retrieval_prompt = self.prompts.get_retrival_prompt(parsed_prompt)
            queries_json = self.ai_service.ask(retrieval_prompt)
            queries = json.loads(queries_json)

            data = []
            for query in queries:
                data.append(self.search_service.search(query))

            generation_prompt = self.prompts.get_generation_prompt(data, parsed_prompt)
            generated_test = self.ai_service.ask(generation_prompt)

            return generated_test
        else:
            raise ValueError("Prompt classification failed. Unrecognized prompt format.")