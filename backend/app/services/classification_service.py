from backend.app.services.ai_service import AiService
from backend.app.models.prompts import SystemPrompts

class ClassificationService:
    def __init__():
        self.prompts = SystemPrompts()
        self.ai_service = AiService()

    def classify(self, text: str):
        return ai_service.ask(prompts.get_classification_prompts(text))