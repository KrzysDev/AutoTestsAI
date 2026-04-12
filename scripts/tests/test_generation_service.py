from backend.app.services.test_generator_service import TestGeneratorService
from backend.app.models.prompts import SystemPrompts


service = TestGeneratorService()

prompts = SystemPrompts()

prompt = input(">")


test = service.generate_test(prompt, "B2", "teens", 20)

print(test)





