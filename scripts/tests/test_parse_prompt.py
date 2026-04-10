from backend.app.services.prompt_parser_service import PromptParserService


service = PromptParserService()


prompt = service.parse_prompt("Wygeneruj test")

print(prompt)