from backend.app.services.prompt_parser_service import PromptParserService


service = PromptParserService()


prompt = service.parse_prompt("Wygeneruj test dla 4 klasy liceum zawierajacy po 1 zadaniu z kazdego czasu w jezyku angielskim. Niech bedzie on roznorodny i powtorzeniowy")

print(prompt)