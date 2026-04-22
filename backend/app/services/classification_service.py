from backend.app.services.ai_service import AiService
from backend.app.models.prompts import SystemPrompts

# <summary>
# Service responsible for classifying user prompts into specific handling strategies.
# </summary>
class ClassificationService:
    def __init__(self, ai_service: AiService):
        self.prompts = SystemPrompts()
        self.ai_service = ai_service

    def classify(self, text: str):
        return self.ai_service.ask(self.prompts.get_classification_prompts(text))