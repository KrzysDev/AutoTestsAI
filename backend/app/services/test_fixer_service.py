from backend.app.services.ai_service import AiService
from backend.app.models.prompts import SystemPrompts
from backend.app.models.schemas import GeneratedTest
import json

class TestFixerService:
    def __init__(self):
        self.ai_service = AiService()
        self.prompts = SystemPrompts()

    def fix_test(self, test: GeneratedTest, teacher_prompt: str) -> GeneratedTest:
        """
        Fixes the test based on teacher's prompt and returns it as GeneratedTest object.
        """
        fixing_prompt = self.prompts.get_test_fixing_prompt(test, teacher_prompt)
        
        fixed_test_raw = self.ai_service.ask(fixing_prompt)
        
        fixed_test_json = self.prompts.clean_json_response(fixed_test_raw)
        
        try:
            fixed_test = GeneratedTest(**json.loads(fixed_test_json))
            return fixed_test
        except Exception as e:
            print(f"Error during test fixing: {e}")
            raise ValueError(f"Failed to fix test: {e}")
