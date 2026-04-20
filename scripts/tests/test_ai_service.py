from backend.app.services.ai_service import AiService


service = AiService()

print(service.ask("What is the meaning of life?"))