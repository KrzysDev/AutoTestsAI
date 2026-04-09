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

    def __transform_request_to_prompt(self, topic: str):
        return self.ai_service.ask(self.prompts.get_transform_request_to_prompt(topic))

    def generate_test(self, topic: str):
        transformed_prompt = self.__transform_request_to_prompt(topic)

        print("transformed_prompt", transformed_prompt)
        
        try:
            transformed_prompt = TransformedPrompt.model_validate(json.loads(transformed_prompt))
        except Exception as e:
            raise ValueError(f"Invalid TransformedPrompt: {e}")

        #test sections
        test_sections = []

        for test_section in transformed_prompt.sections:

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
            except ValueError as e:
                print(f"could not transform generated section into json: {generated_section} \n Error: {e}")
                continue

            new_generated_section = GeneratedTestSection(
                instruction=generated_section['Question']['content']['instruction'],
                body=generated_section['Question']['content']['body']
            )

            test_sections.append(new_generated_section)
        
        return test_sections