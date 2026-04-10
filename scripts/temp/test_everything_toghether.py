from backend.app.services.classification_service import ClassificationService
from backend.app.services.prompt_parser_service import PromptParserService
from backend.app.models.prompts import SystemPrompts
import json
from backend.app.models.schemas import ParsedPrompt
from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService


def main():
    classification_service = ClassificationService()
    prompt_parser_service = PromptParserService()
    prompts = SystemPrompts()
    ai_service = AiService()
    search_service = SearchService()


    prompt = input("Podaj prompt > ")
    level: Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] = input("level > ")
    age_group : Literal["kids", "teens", "adults"] = input("age_group > ")


    if classification_service.classify(prompt) == "normal":
        classified_prompt = prompt_parser_service.parse_prompt(prompt)

        json_classified_prompt = json.loads(classified_prompt)

        parsed_prompt = ParsedPrompt(
            task = prompt,
            level = level,
            age_group = age_group,
            sections = json_classified_prompt['sections'],
            total_amount = json_classified_prompt['total_amount']

        )

        prompt2 = prompts.get_retrival_prompt(parsed_prompt)

        queries = ai_service.ask(prompt2)
        
        queries = json.loads(queries)

        print(queries)

        data = []
        
        for query in queries:
            data.append(search_service.search(query))
        
        print("data: ")
        print(data)

        generation_prompt = prompts.get_generation_prompt(data, parsed_prompt)

        generated_test = ai_service.ask(generation_prompt)

        print(generated_test)
        


main()


        