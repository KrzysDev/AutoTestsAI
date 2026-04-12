from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.models.prompts import SystemPrompts
from backend.app.services.embeddings_service import EmbeddingsService
from backend.app.services.json_test_converting_service import JsonTestConvertingService
import json
import ast
from typing import Literal
from backend.app.services.classification_service import ClassificationService
from backend.app.services.prompt_parser_service import PromptParserService
from backend.app.models.schemas import ParsedPrompt, GeneratedTest, PDFTest
import re


# <summary>
# Service responsible for generating educational tests by orchestrating AI and search components.
# Includes classification, prompt parsing, retrieval, and final test generation.
# </summary>
class TestGeneratorService:
    def __init__(self):
        self.ai_service = AiService()
        self.search_service = SearchService()
        self.prompts = SystemPrompts()
        self.embeddings_service = EmbeddingsService()
        self.classification_service = ClassificationService()
        self.prompt_parser_service = PromptParserService()
        self.json_test_converting_service = JsonTestConvertingService()

    def generate_test(self, 
                      prompt: str, 
                      level: Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2'], 
                      age_group: Literal["kids", "teens", "adults"],
                      total_amount: int) -> str:
        """
        Generates a test based on the user prompt and configuration.
        """
        if self.classification_service.classify(prompt) == "normal":
            classified_prompt = self.prompt_parser_service.parse_prompt(prompt)
            json_classified_prompt = json.loads(classified_prompt)

            parsed_prompt = ParsedPrompt(
                task=prompt,
                level=level,
                age_group=age_group,
                sections=json_classified_prompt['sections'],
                total_amount=total_amount
            )

            retrieval_prompt = self.prompts.get_retrival_prompt(parsed_prompt)
            queries_json = self.ai_service.ask(retrieval_prompt)
            queries = json.loads(queries_json)

            data = []

            reading_data = []
            writing_data = []

            reading_enabled = False
            writing_enabled = False

            for query in queries:
                if query.lower() == "reading":
                    reading_data.append(self.search_service.search(query))
                    reading_enabled = True
                
                if query.lower() == "writing":
                    writing_data.append(self.search_service.search(query))
                    writing_enabled = True
                
                data.append(self.search_service.search(query))

            generation_prompt = self.prompts.get_generation_prompt(data, parsed_prompt)
            generated_test_raw = self.ai_service.ask(generation_prompt)
            generated_test_json = self.__clean_json_response(generated_test_raw)
            generated_test = json.loads(generated_test_json)

            if reading_enabled:
                reading_prompt = self.prompts.get_reading_prompt(reading_data, parsed_prompt)
                reading_raw = self.ai_service.ask(reading_prompt)
                reading_json = self.__clean_json_response(reading_raw)
                reading_data_parsed = json.loads(reading_json)

                # Merge exercises lists
                if 'exercises' in generated_test and 'exercises' in reading_data_parsed:
                    generated_test['exercises'].extend(reading_data_parsed['exercises'])
                elif 'exercises' in reading_data_parsed:
                    # Fallback if generated_test has weird structure
                    generated_test = reading_data_parsed

            if writing_enabled:
                writing_prompt = self.prompts.get_writing_prompt(writing_data, parsed_prompt)
                writing_raw = self.ai_service.ask(writing_prompt)
                writing_json = self.__clean_json_response(writing_raw)
                writing_data_parsed = json.loads(writing_json)

                # Merge exercises lists
                if 'exercises' in generated_test and 'exercises' in writing_data_parsed:
                    # If there's an answer key in generated_test, we might want to put writing before it
                    # but simple extend is what reading does
                    generated_test['exercises'].extend(writing_data_parsed['exercises'])
                elif 'exercises' in writing_data_parsed:
                    if not generated_test:
                        generated_test = writing_data_parsed
                    else:
                        generated_test['exercises'] = writing_data_parsed['exercises']

            return json.dumps(generated_test)
        else:
            raise ValueError("Prompt classification failed. Unrecognized prompt format.")

    def generate_beautified_test(self, generated_test_json: str) -> bytes:
        """
        Restructures a raw generated test and converts it to a beautified PDF.
        """
        # Parse the raw test to ensure it's valid
        raw_test_data = json.loads(generated_test_json)
        generated_test = GeneratedTest(**raw_test_data)

        # Get the restructuring prompt
        restructure_prompt = self.prompts.get_test_restructuring_prompt(generated_test)
        
        # Ask AI to restructure
        restructured_raw = self.ai_service.ask(restructure_prompt)
        restructured_json = self.__clean_json_response(restructured_raw)
        
        try:
            # Parse into PDFTest model
            pdf_test = PDFTest(**json.loads(restructured_json))
            
            # Convert to PDF
            pdf_bytes = self.json_test_converting_service.convert_to_pdf(pdf_test)
            return pdf_bytes
        except Exception as e:
            # Fallback or error handling
            print(f"Error during restructuring or PDF generation: {e}")
            raise ValueError(f"Failed to generate beautified PDF: {e}")

    def __clean_json_response(self, response: str) -> str:
        """
        Cleans the AI response by removing markdown code blocks and extra text.
        """
        # Remove markdown code blocks like ```json ... ```
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            return json_match.group(1).strip()
        
        # If no code block, try to find the first '{' or '[' and last '}' or ']'
        start_idx = response.find('{')
        if start_idx == -1:
            start_idx = response.find('[')
            
        end_idx = response.rfind('}')
        if end_idx == -1:
            end_idx = response.rfind(']')
            
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return response[start_idx:end_idx + 1].strip()
            
        return response.strip()