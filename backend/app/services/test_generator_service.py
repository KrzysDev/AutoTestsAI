from backend.app.services.ai_service import AiService
from backend.app.models.prompts_v2 import SystemPrompts
from backend.app.models.schemas import RetrivedChunk, Group, Test
from backend.app.services.search_service import SearchService
from typing import Literal
import json

class TestGeneratorService:

    def __init__(self):
        self.ai_service = AiService()
        self.prompts = SystemPrompts()
        self.search_service = SearchService()

    def __generate_query_requests(self, language: str, level: str, topic: str) -> list[str]:
        raw = self.ai_service.ask_ollama_cloud(self.prompts.get_queries_prompt(language, level, topic), 'gpt-oss:20b')
        return json.loads(raw)

    def __retrive_data(self, questions: list[str]) -> list[RetrivedChunk]:
        unique_chunks = []
        seen = set()

        for question in questions:
            chunks = self.search_service.search(question, top_k=5)
            for chunk in chunks:
                key = f"{chunk.payload.metadata.subject}:{chunk.payload.metadata.content}"
                if key not in seen:
                    seen.add(key)
                    unique_chunks.append(chunk)
            
        return unique_chunks
    
    def __generate_plan(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], topic: str, retrieved_chunks: list[RetrivedChunk]) -> str:
        return self.ai_service.ask_ollama_cloud(self.prompts.get_plan_test_creation_prompt(language, level, topic, retrieved_chunks), 'gpt-oss:120b')
    
    def __generate_group(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], topic: str, plan: str) -> str:
        return self.ai_service.ask_ollama_cloud(self.prompts.get_test_creation_prompt(language, level, topic, plan), 'gpt-oss:120b')

    def __generate_another_group(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], topic: str, previous_group: Group) -> str:
        return self.ai_service.ask_ollama_cloud(self.prompts.get_another_group_prompt(language, level, previous_group.model_dump_json(), topic), 'gpt-oss:120b')

    def generate_all_groups(self, 
        language: str, 
        level: str, 
        topic: str,
        group_count: int = 2) -> Test:

        queries = self.__generate_query_requests(language, level, topic)
        print("queries:", queries)
        print("========================================================")

        retrieved_chunks = self.__retrive_data(queries)
        print("retrieved chunks:", retrieved_chunks)
        print("========================================================")

        plan = self.__generate_plan(language, level, topic, retrieved_chunks)
        print("plan:", plan)
        print("========================================================")

        first_group_raw = self.__generate_group(language, level, topic, plan)
        print("first group raw:", first_group_raw)
        print("========================================================")



        count = 0
        all_groups = []

        while count < group_count:
            try:
                if count == 0:
                    group = Group.model_validate_json(first_group_raw)
                else:
                    raw = self.__generate_another_group(language, level, topic, all_groups[-1])
                    group = Group.model_validate_json(raw)

                all_groups.append(group)
                count += 1

            except Exception as e:
                print(f"Error validating group {count}: {e}")
                break

        test = Test(groups=all_groups)
        return test