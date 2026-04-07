from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.models.prompts import SystemPrompts

from backend.app.models.schemas import Test, Question, AgenticPromptSecondLayer, AgenticPromptFirstLayer, TransformedPrompt

import json

class TestGeneratorService:
    def __init__(self):
        self.ai_service = AiService()
        self.search_service = SearchService()
        self.prompts = SystemPrompts()

    def __transform_request_to_prompt(self, topic: str):
        return self.ai_service.ask(self.prompts.get_transform_request_to_prompt(topic))

    def generate_test(self, topic: str):
        transformed_prompt = self.__transform_request_to_prompt(topic)

        print("transformed_prompt", transformed_prompt)
        
        try:
            transformed_prompt = TransformedPrompt.model_validate(transformed_prompt)
        except Exception as e:
            raise ValueError(f"Invalid TransformedPrompt: {e}")

        #retrive chunks based on transformed prompt data

        #create new generation prompt with retrived data for each exercise

        #for each exercise in exercices AiCreate()

        #exercise.append and tests.extend

        

       
        print("first_layer_prompt", first_layer_prompt.model_dump_json(indent=4))       
