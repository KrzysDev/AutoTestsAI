from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.models.prompts import SystemPrompts
from backend.app.models.schemas import Test, Question, TransformedPrompt, TestSection, RetrievalData, RetrievalInstructions, RetrivedChunk
from backend.app.services.embeddings_service import EmbeddingsService
import json
import time

class TestGeneratorService:
    def __init__(self):
        self.ai_service = AiService()
        self.search_service = SearchService()
        self.prompts = SystemPrompts()
        self.embeddings_service = EmbeddingsService()

    def __transform_request_to_prompt(self, topic: str):
        return self.ai_service.ask(self.prompts.get_transform_request_to_prompt(topic))

    def generate_test(self, topic: str):
        transformed_prompt = self.__transform_request_to_prompt(topic)

        print("transformed_prompt", transformed_prompt)
        
        try:
            transformed_prompt = TransformedPrompt.model_validate(json.loads(transformed_prompt))
        except Exception as e:
            raise ValueError(f"Invalid TransformedPrompt: {e}")

        #retrive chunks based on transformed prompt data

        grammar_inst = []
        exercise_inst = []

        for test_section in transformed_prompt.sections:

            embedding = self.embeddings_service.embed_text(
                f"{test_section.section_type}, {test_section.subject}"
            )

            instruction_records = self.search_service.search_with_filter(
                "Grammar Collection", "type", "exam-task-instruction", embedding, 3
            )

            grammar_records = self.search_service.search_with_filter(
                "Grammar Collection", "type", "grammar", embedding, 3
            )

            for grammar_record in grammar_records:
                grammar_inst.append(RetrivedChunk(
                    payload=grammar_record.payload,
                    score = None
                ))
            for instruction_record in instruction_records:
                exercise_inst.append(RetrivedChunk(
                    payload = instruction_record.payload,
                    score = None
                ))
        

                #create new generation prompt with retrived data for each exercise

        retrieval_data = RetrievalData(
            instructions=RetrievalInstructions(
                grammar_instructions=grammar_inst,
                exercise_instructions=exercise_inst
            )
        )

        generation_prompt = self.prompts.get_section_generation_prompt(retrieval_data, transformed_prompt)

        print(generation_prompt)

        time.sleep(10)

        #for each exercise in exercices AiCreate()

        #exercise.append and tests.extend    
