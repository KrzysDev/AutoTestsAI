from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.models.prompts import SystemPrompts
from backend.app.services.json_test_converting_service import JsonTestConvertingService
import json
import ast
from typing import Literal
from backend.app.services.classification_service import ClassificationService
from backend.app.services.prompt_parser_service import PromptParserService
from backend.app.models.schemas import ParsedPrompt, GeneratedTest, PDFTest, TestGeneratorResponse, TestGeneratorResponseMetadata, TestGeneratorResponseMetadataRetrival, Exercise, Form, TestGeneratorHTMLResponse
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

    def generate_test_from_prompt(self, prompt: str) -> TestGeneratorResponse:
        """
        Generates a test based on the user prompt.
        """
        start = time.time()
        total_tokens = 0
        
        # 1. Classification
        classification_prompt = self.prompts.get_classification_prompts(prompt)
        total_tokens += self.__count_tokens(classification_prompt)
        classification : str = self.ai_service.ask_model(classification_prompt, "gemma4:31b-cloud")
        total_tokens += self.__count_tokens(classification)

        if "request" in classification.lower():
            parsing_prompt = self.prompts.get_parsing_prompt(prompt)
            parsed_prompt, tokens_used = self.__ask_model_for_json(parsing_prompt, "gemma4:31b-cloud", ParsedPrompt)
            total_tokens += tokens_used

            data, reading_data, writing_data, reading_enabled, writing_enabled, retrival_metadata = self.__perform_retrieval(parsed_prompt.sections)

            combined_prompt = self.prompts.get_combined_generation_prompt(
                retrieval=data,
                reading_data=reading_data,
                writing_data=writing_data,
                parsed_prompt=parsed_prompt,
                reading_enabled=reading_enabled,
                writing_enabled=writing_enabled
            )
            
            checked_generated_test, tokens_used_gen = self.__generate_and_check_json_test(combined_prompt, parsed_prompt)
            total_tokens += tokens_used_gen

            metadata = self.__build_metadata(start, prompt, parsed_prompt.model_dump_json(), total_tokens, retrival_metadata)

            return TestGeneratorResponse(
                response=checked_generated_test,
                metadata=metadata
            )
        else:
            res = self.ai_service.ask(self.prompts.get_general_question_prompt(prompt))
            gen_prompt = self.prompts.get_general_question_prompt(prompt)
            
            timer = time.time() - start
            average_time = self.__get_and_update_average_time(timer)
            metadata = TestGeneratorResponseMetadata(
                prompt=prompt,
                parsed_prompt="general",
                tokens=self.__count_tokens(res) + self.__count_tokens(gen_prompt),
                time=timer,
                average_time=average_time,
                retrival=TestGeneratorResponseMetadataRetrival(regular="", writing="", reading="")
            )
            return TestGeneratorResponse(
                response=GeneratedTest(exercises=[Exercise(instruction="AI Response", body=res)]),
                metadata=metadata
            )

    def generate_test_from_survey(self, form: Form) -> TestGeneratorResponse:
        """
        Generates a test based on the structured survey form, skipping the AI classification and parsing steps.
        """
        print("generate_test_from_survey start")
        start = time.time()
        
        data, reading_data, writing_data, reading_enabled, writing_enabled, retrival_metadata = self.__perform_retrieval(form.sections)

        combined_prompt = self.prompts.get_combined_generation_prompt(
            retrieval=data,
            reading_data=reading_data,
            writing_data=writing_data,
            parsed_prompt=form,
            reading_enabled=reading_enabled,
            writing_enabled=writing_enabled
        )
        
        checked_generated_test, total_tokens = self.__generate_and_check_json_test(combined_prompt, form)

        metadata = self.__build_metadata(start, "Survey Generated Test", form.model_dump_json(), total_tokens, retrival_metadata)

        return TestGeneratorResponse(
            response=checked_generated_test,
            metadata=metadata
        )

    def generate_html_test_from_prompt(self, prompt: str):
        """
        Generates an HTML test based on the user prompt. Includes AI classification.
        """
        print("generate_html_test_from_prompt start")
        start = time.time()
        total_tokens = 0

        # 1. Classification
        classification_prompt = self.prompts.get_classification_prompts(prompt)
        total_tokens += self.__count_tokens(classification_prompt)
        classification : str = self.ai_service.ask_model(classification_prompt, "gemma4:31b-cloud")
        total_tokens += self.__count_tokens(classification)

        if "request" in classification.lower():
            parsing_prompt = self.prompts.get_parsing_prompt(prompt)
            parsed_prompt, tokens_used = self.__ask_model_for_json(parsing_prompt, "gemma4:31b-cloud", ParsedPrompt)
            total_tokens += tokens_used

            data, reading_data, writing_data, reading_enabled, writing_enabled, retrival_metadata = self.__perform_retrieval(parsed_prompt.sections)

            combined_prompt = self.prompts.get_combined_html_generation_prompt(
                retrieval=data,
                reading_data=reading_data,
                writing_data=writing_data,
                parsed_prompt=parsed_prompt,
                reading_enabled=reading_enabled,
                writing_enabled=writing_enabled
            )
            total_tokens += self.__count_tokens(combined_prompt)
            
            generated_test_raw = self.ai_service.ask(combined_prompt)
            total_tokens += self.__count_tokens(generated_test_raw)
            
            metadata = self.__build_metadata(start, prompt, parsed_prompt.model_dump_json(), total_tokens, retrival_metadata)

            return TestGeneratorHTMLResponse(
                response=generated_test_raw,
                metadata=metadata
            )
        else:
            gen_prompt = self.prompts.get_general_question_prompt(prompt)
            res = self.ai_service.ask(self.prompts.get_general_question_prompt(gen_prompt))
            
            timer = time.time() - start
            average_time = self.__get_and_update_average_time(timer)
            metadata = TestGeneratorResponseMetadata(
                prompt=prompt,
                parsed_prompt="general",
                tokens=total_tokens + self.__count_tokens(res) + self.__count_tokens(gen_prompt),
                time=timer,
                average_time=average_time,
                retrival=TestGeneratorResponseMetadataRetrival(regular="", writing="", reading="")
            )
            
            return TestGeneratorHTMLResponse(
                response=res,
                metadata=metadata
            )

    def generate_html_test_from_survey(self, form: Form) -> TestGeneratorHTMLResponse:
        """
        Generates an HTML test based on the structured survey form.
        """
        print("generate_html_test_from_survey start")
        start = time.time()
        total_tokens = 0

        data, reading_data, writing_data, reading_enabled, writing_enabled, retrival_metadata = self.__perform_retrieval(form.sections)

        combined_prompt = self.prompts.get_combined_html_generation_prompt(
            retrieval=data,
            reading_data=reading_data,
            writing_data=writing_data,
            parsed_prompt=form,
            reading_enabled=reading_enabled,
            writing_enabled=writing_enabled
        )
        total_tokens += self.__count_tokens(combined_prompt)
        
        generated_test_raw = self.ai_service.ask(combined_prompt)
        total_tokens += self.__count_tokens(generated_test_raw)
        
        metadata = self.__build_metadata(start, "Survey Generated HTML Test", form.model_dump_json(), total_tokens, retrival_metadata)

        return TestGeneratorHTMLResponse(
            response=generated_test_raw,
            metadata=metadata
        )

    # --- Sub-methods for Refactoring ---

    def __ask_model_for_json(self, prompt: str, model: str, schema, max_tries: int = 3) -> tuple:
        total_tokens = self.__count_tokens(prompt)
        for i in range(max_tries):
            raw_response = self.ai_service.ask_model(prompt, model)
            total_tokens += self.__count_tokens(raw_response)
            print(f"__ask_model_for_json (Attempt {i+1}):\n{raw_response}")
            try:
                cleaned = self.__clean_json_response(raw_response)
                parsed_dict = json.loads(cleaned)
                return schema(**parsed_dict), total_tokens
            except (ValueError, json.JSONDecodeError, TypeError) as e:
                print(f"Failed to parse JSON on attempt {i+1}: {e}")
                if i == max_tries - 1:
                    raise ValueError(f"Model returned invalid json: {e}")
        return None, total_tokens

    def __perform_retrieval(self, sections) -> tuple[list, list, list, bool, bool, TestGeneratorResponseMetadataRetrival]:
        data, reading_data, writing_data = [], [], []
        reading_enabled, writing_enabled = False, False
        retrival_metadata = TestGeneratorResponseMetadataRetrival(regular="", writing="", reading="")

        for section in sections:
            query = section.subject
            res = self.search_service.search(query)
            
            if query.lower() == "reading":
                reading_data.append(res)
                retrival_metadata.reading += json.dumps(res) + "\n"
                reading_enabled = True
            elif query.lower() == "writing":
                writing_data.append(res)
                retrival_metadata.writing += json.dumps(res) + "\n"
                writing_enabled = True
            else:
                data.append(res)
                retrival_metadata.regular += json.dumps(res) + "\n"

        return data, reading_data, writing_data, reading_enabled, writing_enabled, retrival_metadata

    def __generate_and_check_json_test(self, combined_prompt: str, check_context) -> tuple[GeneratedTest, int]:
        tokens_used = self.__count_tokens(combined_prompt)
        
        # 1st Pass: Generation
        raw_test = self.ai_service.ask(combined_prompt)
        tokens_used += self.__count_tokens(raw_test)
        cleaned_test = self.__clean_json_response(raw_test)
        try:
            generated_test_dict = json.loads(cleaned_test)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse AI response as JSON: {e}")
            raise ValueError(f"AI returned invalid JSON. Error: {e}. Response preview: {cleaned_test[:200]}")
        
        # 2nd Pass: Checking
        check_prompt = self.prompts.get_test_checking_prompt(GeneratedTest(**generated_test_dict), check_context)
        tokens_used += self.__count_tokens(check_prompt)
        
        checked_test_raw = self.ai_service.ask(check_prompt)
        tokens_used += self.__count_tokens(checked_test_raw)
        cleaned_checked_test = self.__clean_json_response(checked_test_raw)
        
        return GeneratedTest(**json.loads(cleaned_checked_test)), tokens_used

    def __build_metadata(self, start_time: float, prompt: str, parsed_prompt_json: str, total_tokens: int, retrival_metadata: TestGeneratorResponseMetadataRetrival) -> TestGeneratorResponseMetadata:
        elapsed_time = time.time() - start_time
        average_time = self.__get_and_update_average_time(elapsed_time)
        return TestGeneratorResponseMetadata(
            prompt=prompt,
            parsed_prompt=parsed_prompt_json,
            tokens=total_tokens,
            time=elapsed_time,
            average_time=average_time,
            retrival=retrival_metadata
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