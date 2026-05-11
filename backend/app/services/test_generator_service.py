from backend.app.services.ai_service import AiService
from backend.app.services.search_service import SearchService
from backend.app.models.prompts import SystemPrompts
from backend.app.utils.json_utils import clean_json_response
import json
import ast
from typing import Literal
from backend.app.services.classification_service import ClassificationService
from backend.app.services.prompt_parser_service import PromptParserService
from backend.app.services.html_cleaner_service import HtmlCleanerService
from backend.app.models.schemas import ParsedPrompt, TestGeneratorResponseMetadata, Form, TestGeneratorHTMLResponse
import re
import os
import time
import asyncio

"""
# Service responsible for generating educational tests by orchestrating AI and search components.
# Includes classification, prompt parsing, retrieval, and final test generation.
"""
class TestGeneratorService:
    def __init__(
        self,
        ai_service: AiService,
        search_service: SearchService,
        classification_service: "ClassificationService",
        prompt_parser_service: "PromptParserService",
        html_cleaner_service: HtmlCleanerService
    ):
        self.ai_service = ai_service
        self.search_service = search_service
        self.prompts = SystemPrompts()
        self.classification_service = classification_service
        self.prompt_parser_service = prompt_parser_service
        self.cleaner_service = html_cleaner_service
        



    async def generate_html_test_from_prompt(self, prompt: str):
        """
        Generates an HTML test based on the user prompt. Includes AI classification and planning.
        """
        start = time.time()
        total_tokens = 0

        # 1. Classification (Fast)
        classification_start = time.time()
        print("classifying...")
        classification_prompt = self.prompts.get_classification_prompts(prompt)
        # Deepseek flash is very fast and reliable for classification
        classification: str = await self.ai_service.ask(classification_prompt, "google/gemini-3.1-flash-lite")
        total_tokens += self.__count_tokens(classification_prompt) + self.__count_tokens(classification)
        print(f"classified: '{classification}'. Time: {time.time() - classification_start}")

        if "request" in classification.lower():
            # 2. Planning and Parsing (Fast)
            planning_parsing_start = time.time()
            print("planning and parsing...")
            planning_parsing_prompt = self.prompts.get_test_planning_and_parsing_prompt(prompt)
            parsed_prompt, tokens_used = await self.__ask_model_for_json(planning_parsing_prompt, ParsedPrompt, model="anthropic/claude-sonnet-4.6")
            total_tokens += tokens_used
            print(f"planned and parsed. Time: {time.time() - planning_parsing_start}")

            if not parsed_prompt or not parsed_prompt.sections:
                return await self.__handle_general_response(prompt, start, total_tokens)

            # 3. Retrieval (Parallelized)
            retrieval_start = time.time()
            print("retrieving data...")
            retrieval_list = await self.__perform_retrieval(parsed_prompt.sections, language=parsed_prompt.language)
            data_str = "\n---\n".join(retrieval_list)
            print(f"retrieved. Time: {time.time() - retrieval_start}")

            # 4. Consolidated Generation (Fast & One-shot)
            generation_start = time.time()
            print("generating test...")
            combined_prompt = self.prompts.get_combined_html_generation_prompt(
                retrieval=data_str,
                parsed_prompt=parsed_prompt
            )
            total_tokens += self.__count_tokens(combined_prompt)
            generated_test = await self.ai_service.ask(combined_prompt, "google/gemini-3.1-flash-lite")
            total_tokens += self.__count_tokens(generated_test)
            print(f"generated. Time: {time.time() - generation_start}")

            # 5. Fast Checking
            checking_start = time.time()
            print("checking...")
            checking_prompt = self.prompts.get_checking_prompt(generated_test, prompt)
            check_result = await self.ai_service.ask(checking_prompt, "anthropic/claude-sonnet-4.6")
            total_tokens += self.__count_tokens(check_result)
            print(f"checked. Time: {time.time() - checking_start}")

            # 6. Optional Fixing
            if check_result.strip().upper() != "OK":
                fixing_start = time.time()
                print("fixing...")
                fixing_prompt = self.prompts.get_fixing_prompt(generated_test, check_result)
                generated_test = await self.ai_service.ask(fixing_prompt, "google/gemini-3.1-pro-preview")
                total_tokens += self.__count_tokens(generated_test)
                print(f"fixed. Time: {time.time() - fixing_start}")
            
            generated_test = self.cleaner_service.clean(generated_test)
            metadata = self.__build_metadata(start, prompt, parsed_prompt.model_dump_json(), total_tokens, data_str)
            
            return TestGeneratorHTMLResponse(response=generated_test, metadata=metadata)
        else:
            return await self.__handle_general_response(prompt, start, total_tokens)

    async def __handle_general_response(self, prompt: str, start: float, total_tokens: int):
        print("generating general response...")
        gen_prompt = self.prompts.get_general_question_prompt(prompt)
        res = await self.ai_service.ask(gen_prompt, "google/gemini-3.1-flash-lite")
        
        timer = time.time() - start
        metadata = TestGeneratorResponseMetadata(
            response_type = "general",
            prompt=prompt,
            parsed_prompt="general",
            tokens=total_tokens + self.__count_tokens(res) + self.__count_tokens(gen_prompt),
            time=timer,
            average_time=self.__get_and_update_average_time(timer),
            retrieval=""
        )
        return TestGeneratorHTMLResponse(response=res, metadata=metadata)

    async def generate_html_test_from_survey(self, form: Form) -> TestGeneratorHTMLResponse:

        """
        Generates an HTML test based on the structured survey form.
        """
        print("generate_html_test_from_survey start")
        start = time.time()
        total_tokens = 0

        # 3. Retrieval (Renumbered from 4)
        retrieval_start = time.time()
        print("retrieving data (Survey)...")
        retrieval_list = await self.__perform_retrieval(
            form.sections, language=form.language
        )
        data_str = "\n---\n".join(retrieval_list)
        print("retrieved (Survey). Time: ", time.time() - retrieval_start)

        # 4. Generation (Fast & One-shot)
        generation_start = time.time()
        print("generating test (Survey)...")
        combined_prompt = self.prompts.get_combined_html_generation_prompt(
            retrieval=data_str,
            parsed_prompt=form
        )
        total_tokens += self.__count_tokens(combined_prompt)
        
        # Using flash for survey generation too
        generated_test_raw = await self.ai_service.ask(combined_prompt, "google/gemini-3.1-pro-preview")
        total_tokens += self.__count_tokens(generated_test_raw)
        print(f"generated (Survey). Time: {time.time() - generation_start}")

        # 5. Fast Checking
        checking_start = time.time()
        print("pedagogical checking (Survey)...")
        checking_prompt = self.prompts.get_checking_prompt(generated_test_raw, "Survey Generated HTML Test")
        check_result = await self.ai_service.ask(checking_prompt, "anthropic/claude-sonnet-4.6")
        total_tokens += self.__count_tokens(check_result)
        print(f"checked (Survey). Time: {time.time() - checking_start}")

        # 6. Optional Fixing
        if not check_result.strip().upper().startswith("OK"):
            fixing_start = time.time()
            print("Fixing test based on pedagogical feedback (Survey)...")
            fixing_prompt = self.prompts.get_fixing_prompt(generated_test_raw, check_result)
            generated_test_raw = await self.ai_service.ask(fixing_prompt, "anthropic/claude-sonnet-4.6")
            total_tokens += self.__count_tokens(generated_test_raw)
            print(f"fixed (Survey). Time: {time.time() - fixing_start}")
        
        generated_test_raw = self.cleaner_service.clean(generated_test_raw)

        
        metadata = self.__build_metadata(start, form.model_dump_json(), form.model_dump_json(), total_tokens, data_str)

        return TestGeneratorHTMLResponse(
            response=generated_test_raw,
            metadata=metadata
        )

    # --- Sub-methods for Refactoring ---

    async def __ask_model_for_json(self, prompt: str, schema, max_tries: int = 3, model: str = "google/gemini-3.1-flash-lite") -> tuple:
        total_tokens = self.__count_tokens(prompt)
        for i in range(max_tries):
            raw_response = await self.ai_service.ask(prompt, model)
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

    async def __perform_retrieval(self, sections, language: str = "en") -> list:
        tasks = [
            self.search_service.search(subject=section.retrival_subject, language=language)
            for section in sections
        ]
        
        results = await asyncio.gather(*tasks)
        
        retrieval_data = []
        for result in results:
            if result:
                retrieval_data.append(json.dumps(result))
        
        return retrieval_data





    def __build_metadata(self, start_time: float, prompt: str, parsed_prompt_json: str, total_tokens: int, retrieval_data: str) -> TestGeneratorResponseMetadata:
        elapsed_time = time.time() - start_time
        average_time = self.__get_and_update_average_time(elapsed_time)
        return TestGeneratorResponseMetadata(
            response_type = "request",
            prompt=prompt,
            parsed_prompt=parsed_prompt_json,
            tokens=total_tokens,
            time=elapsed_time,
            average_time=average_time,
            retrieval=retrieval_data
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