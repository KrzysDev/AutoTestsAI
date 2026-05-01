from backend.app.models.prompts import SystemPrompts


prompts = SystemPrompts()


print(prompts.get_classification_prompts("Dupa dupa kamieni kupa"))