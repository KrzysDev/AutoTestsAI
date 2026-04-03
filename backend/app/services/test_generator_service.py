from backend.app.services.ai_service import AiService
from backend.app.models.schemas import Test, Chunk
from backend.app.models.prompts import SystemPrompts
from backend.app.services.search_service import SearchService
from typing import Literal

class TestGeneratorService:
    def __init__(self):
        self.ai_service = AiService()
        self.prompts = SystemPrompts()
        self.search_service = SearchService()

    def __plan_test(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], topic: str) -> Test:
        prompt = self.prompts.get_test_planning_prompt(language, level, topic)
        return self.ai_service.ask_ollama_cloud(prompt)

    def __generate_query_requests(self, plan: str) -> list[str]:
        return self.ai_service.ask_ollama_cloud(self.prompts.get_query_requests_prompt(plan)).split('\n')

    def __retrive_data(self, questions: list[str]) -> List[Chunk]:
        answers = []
        for question in questions:
            answers.append(self.search_service.search(question, top_k=5))

        #in some queries data may occur more than once. So we leave only unice chunks to not make prompt to big
        answers = set(answers)
        answers = list(answers)

        
        return answers

    def generate_test(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], topic: str) -> Test:
        classification = self.ai_service.classify_text(topic)

        #print(classification)

        if classification == "test":
            plan = self.__plan_test(language, level, topic)
            query_requests = self.__generate_query_requests(plan)

            data = self.__retrive_data(query_requests)
            
        else:
            print("no plan, because question is general")

        
        
