from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.models.prompts import SystemPrompts
from backend.app.utils.json_utils import clean_json_response
import json
import ast
from typing import Literal
from backend.app.services.classification_service import ClassificationService
from backend.app.services.prompt_parser_service import PromptParserService
from backend.app.models.schemas import ParsedPrompt, TestGeneratorResponseMetadata, TestGeneratorResponseMetadataRetrival, Form, TestGeneratorHTMLResponse
import re
import os
import time

# <summary>
# Service responsible for generating educational tests by orchestrating AI and search components.
# Includes classification, prompt parsing, retrieval, and final test generation.
# </summary>
class TestGeneratorService:
    def __init__(
        self,
        ai_service: AiService,
        search_service: SearchService,
        classification_service: "ClassificationService",
        prompt_parser_service: "PromptParserService",
    ):
        self.ai_service = ai_service
        self.search_service = search_service
        self.prompts = SystemPrompts()
        self.classification_service = classification_service
        self.prompt_parser_service = prompt_parser_service



    def generate_html_test_from_prompt(self, prompt: str):
        """
        Generates an HTML test based on the user prompt. Includes AI classification.
        """
        start = time.time()
        total_tokens = 0

        # 1. Classification
        classification_time = time.time()
        print("classifying...")
        classification_prompt = self.prompts.get_classification_prompts(prompt)
        total_tokens += self.__count_tokens(classification_prompt)
        classification : str = self.ai_service.ask(classification_prompt, "deepseek/deepseek-v4-flash")
        total_tokens += self.__count_tokens(classification)

        print("classified. Time: ", time.time() - classification_time)
        
        if "request" in classification.lower():
            # 2. Planning
            planning_start = time.time()
            print("planning...")
            planning_prompt = self.prompts.get_test_plan_prompt(prompt)
            planned_response = self.ai_service.ask(planning_prompt, "anthropic/claude-sonnet-4")
            print("planned. Time: ", time.time() - planning_start)

            # 3. Parsing
            parsing_start = time.time()
            print("parsing...")
            parsing_prompt = self.prompts.get_parsing_prompt(planned_response)
            parsed_prompt, tokens_used = self.__ask_model_for_json(parsing_prompt, ParsedPrompt)
            total_tokens += tokens_used
            print("parsed. Time: ", time.time() - parsing_start)

            # 4. Retrieval
            retrieval_start = time.time()
            print("retrieving data...")
            data, reading_data, writing_data, reading_enabled, writing_enabled, retrival_metadata = self.__perform_retrieval(
                parsed_prompt.sections, language=parsed_prompt.language
            )
            print("retrieved. Time: ", time.time() - retrieval_start)
            print("retrived_data: ", data)

            # 5. Generation
            generation_start = time.time()
            print("generating test...")
            combined_prompt = self.prompts.get_combined_html_generation_prompt(
                retrieval=data,
                reading_data=reading_data,
                writing_data=writing_data,
                parsed_prompt=parsed_prompt,
                reading_enabled=reading_enabled,
                writing_enabled=writing_enabled
            )

            total_tokens += self.__count_tokens(combined_prompt)
            
            generated_test_raw = self.ai_service.ask(combined_prompt, "deepseek/deepseek-v4-flash")
            total_tokens += self.__count_tokens(generated_test_raw)
            print("generated. Time: ", time.time() - generation_start)

            # 6. Checking Stage
            checking_start = time.time()
            print("pedagogical checking...")
            checking_prompt = self.prompts.get_checking_prompt(generated_test_raw, prompt)
            check_result = self.ai_service.ask(checking_prompt, "deepseek/deepseek-v4-flash")
            print(f"Pedagogical Check Result:\n{check_result}")
            total_tokens += self.__count_tokens(check_result)
            print("checked. Time: ", time.time() - checking_start)

            # 7. Fixing Stage (if needed)
            if not check_result.strip().upper() == "OK":
                fixing_start = time.time()
                print("Fixing test based on pedagogical feedback...")
                fixing_prompt = self.prompts.get_fixing_prompt(generated_test_raw, check_result)
                generated_test_raw = self.ai_service.ask(fixing_prompt, "deepseek/deepseek-v4-flash")
                total_tokens += self.__count_tokens(generated_test_raw)
                print("fixed. Time: ", time.time() - fixing_start)
            
            metadata = self.__build_metadata(start, prompt, parsed_prompt.model_dump_json(), total_tokens, retrival_metadata)

            return TestGeneratorHTMLResponse(
                response=generated_test_raw,
                metadata=metadata
            )
        else:
            general_start = time.time()
            print("generating general response...")
            gen_prompt = self.prompts.get_general_question_prompt(prompt)
            res = self.ai_service.ask(gen_prompt, "deepseek/deepseek-v4-flash")
            print("general response generated. Time: ", time.time() - general_start)
            
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

        # 4. Retrieval
        retrieval_start = time.time()
        print("retrieving data (Survey)...")
        data, reading_data, writing_data, reading_enabled, writing_enabled, retrival_metadata = self.__perform_retrieval(
            form.sections, language=form.language
        )
        print("retrieved (Survey). Time: ", time.time() - retrieval_start)

        # 5. Generation
        generation_start = time.time()
        print("generating test (Survey)...")
        combined_prompt = self.prompts.get_combined_html_generation_prompt(
            retrieval=data,
            reading_data=reading_data,
            writing_data=writing_data,
            parsed_prompt=form,
            reading_enabled=reading_enabled,
            writing_enabled=writing_enabled
        )
        total_tokens += self.__count_tokens(combined_prompt)
        
        generated_test_raw = self.ai_service.ask(combined_prompt, "anthropic/claude-sonnet-4")
        total_tokens += self.__count_tokens(generated_test_raw)
        print("generated (Survey). Time: ", time.time() - generation_start)

        # 6. Checking Stage
        checking_start = time.time()
        print("pedagogical checking (Survey)...")
        checking_prompt = self.prompts.get_checking_prompt(generated_test_raw, "Survey Generated HTML Test")
        check_result = self.ai_service.ask(checking_prompt, "deepseek/deepseek-v4-flash")
        print(f"Pedagogical Check Result (Survey):\n{check_result}")
        total_tokens += self.__count_tokens(check_result)
        print("checked (Survey). Time: ", time.time() - checking_start)

        # 7. Fixing Stage (if needed)
        if not check_result.strip().upper().startswith("OK"):
            fixing_start = time.time()
            print("Fixing test based on pedagogical feedback (Survey)...")
            fixing_prompt = self.prompts.get_fixing_prompt(generated_test_raw, check_result)
            generated_test_raw = self.ai_service.ask(fixing_prompt, "anthropic/claude-sonnet-4")
            total_tokens += self.__count_tokens(generated_test_raw)
            print("fixed (Survey). Time: ", time.time() - fixing_start)
        
        metadata = self.__build_metadata(start, "Survey Generated HTML Test", form.model_dump_json(), total_tokens, retrival_metadata)

        return TestGeneratorHTMLResponse(
            response=generated_test_raw,
            metadata=metadata
        )

    # --- Sub-methods for Refactoring ---

    def __ask_model_for_json(self, prompt: str, schema, max_tries: int = 3, model: str = "deepseek/deepseek-v4-flash") -> tuple:
        total_tokens = self.__count_tokens(prompt)
        for i in range(max_tries):
            raw_response = self.ai_service.ask(prompt, model)
            total_tokens += self.__count_tokens(raw_response)
            print(f"__ask_model_for_json (Attempt {i+1}):\n{raw_response}")
            try:
                cleaned = clean_json_response(raw_response)
                parsed_dict = json.loads(cleaned)
                return schema(**parsed_dict), total_tokens
            except (ValueError, json.JSONDecodeError, TypeError) as e:
                print(f"Failed to parse JSON on attempt {i+1}: {e}")
                if i == max_tries - 1:
                    raise ValueError(f"Model returned invalid json: {e}")
        return None, total_tokens

    def __perform_retrieval(self, sections, language: str = "en") -> tuple[list, list, list, bool, bool, TestGeneratorResponseMetadataRetrival]:
        data, reading_data, writing_data = [], [], []
        reading_enabled, writing_enabled = False, False
        retrival_metadata = TestGeneratorResponseMetadataRetrival(regular="", writing="", reading="")

        for section in sections:
            query = section.retrival_subject
            
            if section.task_type == "reading":
                res = self.search_service.search(query, language=language)
                reading_data.append(res)
                retrival_metadata.reading += json.dumps(res) + "\n"
                reading_enabled = True
            elif section.task_type == "writing":
                res = self.search_service.search(query, language=language)
                writing_data.append(res)
                retrival_metadata.writing += json.dumps(res) + "\n"
                writing_enabled = True
            else:
                res = self.search_service.search(query, language=language)
                data.append(res)
                retrival_metadata.regular += json.dumps(res) + "\n"

        return data, reading_data, writing_data, reading_enabled, writing_enabled, retrival_metadata



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