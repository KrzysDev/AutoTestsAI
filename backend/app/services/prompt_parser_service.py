from backend.app.services.ai_service import AiService

from backend.app.models.schemas import ParsedPrompt, PromptTestSection

from backend.app.models.prompts import SystemPrompts

class PromptParserService:

    def __init__(self):

        self.ai_service =AiService()

        self.prompts = SystemPrompts()


    def parse_prompt(self, text: str):

        return self.ai_service.ask(self.prompts.get_parsing_prompt(text))