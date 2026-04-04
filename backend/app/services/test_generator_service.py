from backend.app.services.ai_service import AiService
from backend.app.models.schemas import Test, Chunk, RetrivedChunk
from backend.app.models.prompts import SystemPrompts
from backend.app.services.search_service import SearchService
from typing import Literal
import json

class TestGeneratorService:
    def __init__(self):
        self.ai_service = AiService()
        self.prompts = SystemPrompts()
        self.search_service = SearchService()

    def __plan_test(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], topic: str) -> Test:
        prompt = self.prompts.get_test_planning_prompt(language, level, topic)
        return self.ai_service.ask_ollama_local(prompt)

    def __generate_query_requests(self, plan: str) -> list[str]:
        return self.ai_service.ask_ollama_local(self.prompts.get_query_requests_prompt(plan)).split('\n')

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

    def generate_test(self, language: Literal["en", "de"] = "en", level: Literal["A1", "A2", "B1", "B2", "C1", "C2"] = "B2", topic: str = "-", group_count: Literal[1,2,3,4] = 2):
        classification = self.ai_service.classify_text(topic)

        if classification == "test":
            plan = self.__plan_test(language, level, topic)
            print(plan)
            query_requests = self.__generate_query_requests(plan)
            print(query_requests)
            data = self.__retrive_data(query_requests)
            print(f"data: {data[:10]}...")

            prompt = self.prompts.get_test_generation_prompt(language, level, data, plan, topic, group_count)
            
            answer = self.ai_service.ask_ollama_cloud(prompt, model='gpt-oss:120b')

            attempts = 0
            json_answer = None

            ##TODO: smaller models make planning pretty well, so we can send requests to them in the future.
            
            while attempts < 4:
                validated_answer = self.ai_service.ask_ollama_cloud(self.prompts.get_test_validation_prompt(answer), model='gpt-oss:120b')    
                
                try:
                    json_answer = json.loads(validated_answer)

                    with open("answer.json", "w", encoding="utf-8") as f:
                        json.dump(validated_answer, f, ensure_ascii=False, indent=4)
                    break
                except Exception:
                    attempts += 1
                    answer = validated_answer
                    
            if json_answer is None:
                raise Exception("Nie udało się uzyskać poprawnego formatu JSON po 4 próbach.")

            return json_answer
            
        else:
            return self.ai_service.ask_ollama_cloud(self.prompts.get_general_question_prompt(topic), model='gpt-oss:120b')
        
    def test_planning(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], topic: str) -> Test:
        plan = self.__plan_test(language, level, topic)
        return plan
    def test_retrive_data(self, questions: list[str]) -> list[RetrivedChunk]:
        return self.__retrive_data(questions)



