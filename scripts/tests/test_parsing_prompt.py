from backend.app.models.prompts import SystemPrompts


from backend.app.config.language_configs import get_possible_language_codes

prompts = SystemPrompts()


print(prompts.get_parsing_prompt("testowy prompt"))


print(get_possible_language_codes())

