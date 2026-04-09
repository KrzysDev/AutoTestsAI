from backend.app.services.classification_service import ClassificationService
from backend.app.services.prompt_parser_service import PromptParserService
from backend.app.models.prompts import SystemPrompts
import json
from backend.app.models.schemas import ParsedPrompt

def main():
    classification_service = ClassificationService()
    prompt_parser_service = PromptParserService()
    prompts = SystemPrompts()

    prompt = input("Podaj prompt")

    if classification_service.classify(prompt) == "normal":
        classified_prompt = prompt_parser_service.parse_prompt(prompt)

        json_classified_prompt = json.loads(classified_prompt)

        parsed_prompt = ParsedPrompt(
            task = prompt,
            level = 'B2',
            age_group = "teens",
            sections = json_classified_prompt['sections'],
            total_amount = json_classified_prompt['total_amount']

        )

        prompt2 = prompts.get_retrival_prompt(parsed_prompt)

        print(prompt2)


main()


        