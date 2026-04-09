from backend.app.services.ai_service import AiService

from backend.app.models.prompts import SystemPrompts



def main():
    ai_service = AiService()
    prompts = SystemPrompts()

    response = ai_service.ask(prompts.get_classification_prompts(""))
    print(response)


main()
