from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.models.prompts import SystemPrompts
from backend.app.services.json_test_converting_service import JsonTestConvertingService
import json
import ast
from typing import Literal
from backend.app.services.classification_service import ClassificationService
from backend.app.services.prompt_parser_service import PromptParserService
from backend.app.models.schemas import ParsedPrompt, GeneratedTest, PDFTest, TestGeneratorResponse, TestGeneratorResponseMetadata, TestGeneratorResponseMetadataRetrival, Exercise
import re
import os

import time
# <summary>
# Service responsible for generating educational tests by orchestrating AI and search components.
# Includes classification, prompt parsing, retrieval, and final test generation.
# </summary>
class TestGeneratorService:
    def __init__(self):
        self.ai_service = AiService()
        self.search_service = SearchService()
        self.prompts = SystemPrompts()
        self.classification_service = ClassificationService()
        self.prompt_parser_service = PromptParserService()
        self.json_test_converting_service = JsonTestConvertingService()

    def generate_test_from_prompt(self, prompt: str, ) -> TestGeneratorResponse:
        """
        Generates a test based on the user prompt.
        """
        print("function start")

        start = time.time()
        total_tokens = 0
        
        # 1. Classification
        classification_prompt = self.prompts.get_classification_prompts(prompt)

        total_tokens += self.__count_tokens(classification_prompt)
        classification : str = self.ai_service.ask_model(classification_prompt, "gemma4:31b-cloud")
        
        total_tokens += self.__count_tokens(classification)

        if "request" in classification.lower():
            queries = []
            
            data = []

            reading_data = []
            writing_data = []

            reading_enabled = False
            writing_enabled = False

            parsing_prompt = self.prompts.get_parsing_prompt(prompt)

            max_tries = 3
            parsed_prompt = None

            for i in range(max_tries):
                parsed_prompt_raw = self.ai_service.ask_model(parsing_prompt, "gemma4:31b-cloud")
                print(f"Parsed prompt raw response (Attempt {i+1}):\n{parsed_prompt_raw}")
                
                try:
                    cleaned_json = self.__clean_json_response(parsed_prompt_raw)
                    parsed_dict = json.loads(cleaned_json)
                    parsed_prompt = ParsedPrompt(**parsed_dict)
                    break
                except (ValueError, json.JSONDecodeError, TypeError) as e:
                    print(f"Failed to parse JSON on attempt {i+1}: {e}")
                    if i == max_tries - 1:
                        raise ValueError(f"Model returned invalid parsed prompt json: {e}")

            for section in parsed_prompt.sections:
                queries.append(section.subject)

            retrival_metadata = TestGeneratorResponseMetadataRetrival(
                regular="",
                writing="",
                reading=""
            )

            for query in queries:
                if query.lower() == "reading":
                    res = self.search_service.search(query)
                    reading_data.append(res)
                    retrival_metadata.reading += json.dumps(res) + "\n"
                    reading_enabled = True
                
                elif query.lower() == "writing":
                    res = self.search_service.search(query)
                    writing_data.append(res)
                    retrival_metadata.writing += json.dumps(res) + "\n"
                    writing_enabled = True
                else:
                    res = self.search_service.search(query)
                    data.append(res)
                    retrival_metadata.regular += json.dumps(res) + "\n"

            combined_prompt = self.prompts.get_combined_generation_prompt(
                retrieval=data,
                reading_data=reading_data,
                writing_data=writing_data,
                parsed_prompt=parsed_prompt,
                reading_enabled=reading_enabled,
                writing_enabled=writing_enabled
            )
            total_tokens += self.__count_tokens(combined_prompt)
            
            gen_start = time.time()
            generated_test_raw = self.ai_service.ask(combined_prompt)
            gen_end = time.time()
            
            total_tokens += self.__count_tokens(generated_test_raw)
            
            generated_test_json = self.__clean_json_response(generated_test_raw)
            
            try:
                generated_test = json.loads(generated_test_json)
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse AI response as JSON: {e}")
                print(f"[ERROR] Full cleaned response: {generated_test_json}")
                raise ValueError(f"AI returned invalid JSON. Error: {e}. Response preview: {generated_test_json[:200]}")

            checked_generated_test_prompt = self.prompts.get_test_checking_prompt(GeneratedTest(**generated_test), parsed_prompt)
            total_tokens += self.__count_tokens(checked_generated_test_prompt)
            
            check_start = time.time()
            checked_generated_test_raw = self.ai_service.ask(checked_generated_test_prompt)
            check_end = time.time()
            total_tokens += self.__count_tokens(checked_generated_test_raw)
            
            checked_generated_test_json = self.__clean_json_response(checked_generated_test_raw)
            checked_generated_test: GeneratedTest = GeneratedTest(**json.loads(checked_generated_test_json))

            end = time.time()
            timer = end - start

            average_time = self.__get_and_update_average_time(timer)

            metadata = TestGeneratorResponseMetadata(
                prompt=prompt,
                parsed_prompt=parsed_prompt.model_dump_json() if parsed_prompt else "",
                tokens=total_tokens,
                time=timer,
                average_time=average_time,
                retrival=retrival_metadata
            )

            return TestGeneratorResponse(
                response=checked_generated_test,
                metadata=metadata
            )
        else:
            res = self.ai_service.ask(self.prompts.get_general_question_prompt(prompt))
            end = time.time()
            timer = end - start
            average_time = self.__get_and_update_average_time(timer)
            
            # For general questions, we wrap the response in a GeneratedTest with one exercise
            gen_prompt = self.prompts.get_general_question_prompt(prompt)
            return TestGeneratorResponse(
                response=GeneratedTest(exercises=[Exercise(instruction="AI Response", body=res)]),
                metadata=TestGeneratorResponseMetadata(
                    prompt=prompt,
                    parsed_prompt="general",
                    tokens=self.__count_tokens(res) + self.__count_tokens(gen_prompt),
                    time=timer,
                    average_time=average_time,
                    retrival=TestGeneratorResponseMetadataRetrival(regular="", writing="", reading="")
                )
            )

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

    def __count_tokens(self, text: str) -> int:
        """
        Estimates the number of tokens in the given text.
        Calculation: 1 word = 1.5 tokens (Gemma model estimate).
        """
        if not text:
            return 0
        word_count = len(text.split())
        return int(word_count * 1.5)

    def __get_and_update_average_time(self, current_time: float) -> float:
        """
        Reads, updates and returns the average response time from statistics/response/average_response_time.json.
        """
        file_path = "statistics/response/average_response_time.json"
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"average": 0.0, "total_requests": 0}
            
            old_avg = data.get("average", 0.0)
            total_req = data.get("total_requests", 0)
            
            new_total_req = total_req + 1
            new_avg = (old_avg * total_req + current_time) / new_total_req
            
            data["average"] = new_avg
            data["total_requests"] = new_total_req
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                
            return new_avg
        except Exception as e:
            print(f"Error updating average response time: {e}")
            return current_time