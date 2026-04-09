from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.models.prompts import SystemPrompts
from backend.app.models.schemas import Test, Question, TransformedPrompt, PromptTestSection, RetrievalData, RetrievalInstructions, RetrivedChunk, Chunk, ChunkMetadata, GeneratedTestSection
from backend.app.services.embeddings_service import EmbeddingsService
import json
import time

class TestGeneratorService:
    def __init__(self):
        self.ai_service = AiService()
        self.search_service = SearchService()
        self.prompts = SystemPrompts()
        self.embeddings_service = EmbeddingsService()

    #helper method
    def __transform_request_to_prompt(self, topic: str):
        return self.ai_service.ask(self.prompts.get_transform_request_to_prompt(topic))

    #helper method with polish prompt, because AI understand polish very good. It tells it to fix the json.
    def __fix_generated_section_with_AI(self, broken_response: str) -> str:
        fix_prompt = f"""Poniższy tekst powinien być poprawnym JSONem w formacie:
            {{"Question": {{"content": {{"instruction": "", "body": ""}}}}}}

            Zwróć WYŁĄCZNIE poprawny JSON, nic więcej. Bez markdown, bez tekstu przed ani po.

            Tekst do naprawy:
            {broken_response}"""
        return self.ai_service.ask(fix_prompt)

    def generate_test(self, topic: str):

        transformed_prompt = self.__transform_request_to_prompt(topic)
        
        try:
            transformed_prompt = TransformedPrompt.model_validate(json.loads(transformed_prompt))
        except Exception as e:
            raise ValueError(f"Invalid TransformedPrompt: {e}")

        test_sections = []

        for test_section in transformed_prompt.sections:
            for i in range(test_section.amount):  
                grammar_inst = []
                exercise_inst = []

                embedding = self.embeddings_service.embed_text(
                    f"{test_section.section_type}, {test_section.subject}"
                )

                grammar_records = self.search_service.get_points_with_subject(test_section.subject)

                instruction_records = self.search_service.search_with_filter(
                    "Grammar Collection", "type", "exam-task-instruction", embedding, 1
                )

                for grammar_record in grammar_records:
                    grammar_inst.append(RetrivedChunk(
                        payload=Chunk(
                            id=str(grammar_record.get("id", "")),
                            section="grammar",                        
                            language=grammar_record.get("language", "en"),
                            level=transformed_prompt.level,          
                            metadata=ChunkMetadata(
                                subject=grammar_record.get("subject", ""),
                                content=grammar_record.get("content", "")  
                            )
                        ),
                        score=None
                    ))
                
                for instruction_record in instruction_records:
                    exercise_inst.append(RetrivedChunk(
                        payload=instruction_record.payload,
                        score=None
                    ))

                retrieval_data = RetrievalData(
                    instructions=RetrievalInstructions(
                        grammar_instructions=grammar_inst,
                        exercise_instructions=exercise_inst
                    )
                )
                generate_exercise_prompt = self.prompts.get_section_generation_prompt(retrieval_data, topic)

                generated_section = self.ai_service.ask(generate_exercise_prompt)

                try:
                    generated_section = json.loads(generated_section)
                except ValueError:
                    print(f"JSON invalid, asking AI to fix...")
                    fixed = self.__fix_generated_section_with_AI(generated_section)
                    try:
                        generated_section = json.loads(fixed)
                    except ValueError as e:
                        print(f"AI could not fix JSON: {e}")
                        continue    

                try:
                    new_generated_section = GeneratedTestSection(
                        instruction=str(generated_section['Question']['content']['instruction']),
                        body=str(generated_section['Question']['content']['body'])
                    )
                except ValueError as e:
                    print(f"error while saving generated section: {e}")

                test_sections.append(new_generated_section)
        
        return test_sections