from backend.app.services.ai_service import AiService
from backend.app.models.schemas import Test
from backend.app.models.prompts import SystemPrompts
from typing import Literal

class TestGeneratorService:
    def __init__(self):
        self.ai_service = AiService()
        self.prompts = SystemPrompts()

    def __plan_test(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], topic: str) -> Test:
        prompt = self.prompts.get_test_planning_prompt(language, level, topic)
        return self.ai_service.ask_ollama_cloud(prompt)

    def generate_test(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], topic: str) -> Test:
        classification = self.ai_service.classify_text(topic)

        print(classification)

        if classification == "test":
            print(self.__plan_test(language, level, topic))
        else:
            print("no plan, because question is general")

        
        
