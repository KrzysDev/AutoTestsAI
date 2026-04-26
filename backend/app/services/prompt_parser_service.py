from backend.app.services.ai_service import AiService

from backend.app.models.languages.schemas import ParsedPrompt, PromptTestSection

from backend.app.models.languages.prompts import SystemPrompts

# <summary>
# Service used to parse natural language prompts into structural models for further processing.
# </summary>
class PromptParserService:

    def __init__(self, ai_service: AiService):

        self.ai_service = ai_service

        self.prompts = SystemPrompts()


    def parse_prompt(self, text: str):

        return self.ai_service.ask(self.prompts.get_parsing_prompt(text))