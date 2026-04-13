from backend.app.models.schemas import ParsedPrompt, PromptTestSection, GeneratedTest, Exercise, PDFTest

# <summary>
# Provides system prompts and templates for instructing the LLMs across various classification, parsing, and generation tasks.
# </summary>
class SystemPrompts:
    def __init__(self):
        pass
    
    def get_classification_prompts(self, text: str):
        return f"""
            # TASK
            You are a classifier for teacher messages in an English exam generation system.

            Your job is to classify the message into exactly ONE category:

            1. "general"
            2. "normal"

            ---

            # DEFINITIONS

            ## 1. "general"
            The message is general and does NOT clearly request creation of a test or exam.

            It may:
            - ask what the system can do
            - ask general questions about teaching or exercises
            - not request a concrete test

            Examples:
            - "What can you generate?"
            - "Can you help with grammar?"
            - "How does this system work?"

            ---

            ## 2. "normal"
            The message clearly requests creation of a test or exam.

            Examples:
            - "Create an English test for high school students."
            - "Make me a grammar test for B1 level."
            - "Prepare a reading comprehension exam."

            Even if some details are present, if the request is incomplete → "normal".

            ---

            # OUTPUT RULES

            - Output ONLY one word
            - No punctuation
            - No explanations
            - No extra text

            Allowed outputs:
            - general
            - normal

            ---

            ## TEACHER REQUEST
            {text}
            """

    def get_parsing_prompt(self, text: str):
        return f"""
            # TASK
            You are a specialist in planning English tests.

            Your task is to extract all necessary information from the teacher's input and return it in the required JSON format.

            ---

            # OUTPUT FORMAT
            You must strictly follow this JSON structure:

            #RULES OF FIELDS
            'task' - teachers request 
            'level' - CEFR level write ONLY ('A1', 'A2'......'C1', 'C2')
            -'age_group' - you can choose only one from those - kids, teens, adults.
            -'sections' - TestSections where task type is ONLY vocabulary, grammar, reading or writing. amount represents how many such sections occur in the test.
            -total_amount - how many exercises in total
            

            {PromptTestSection.model_json_schema()}

            ---

            # RULES
            - You MUST return ONLY valid JSON.
            - Do NOT include any explanations.
            - Do NOT include markdown formatting (e.g. ```json, ```).
            - Do NOT add any extra text before or after the JSON.
            - You MUST use double quotes for all keys and string values.
            - The output must strictly match the provided schema (no missing or extra fields).
            - If information is missing, use null or empty values where appropriate (according to schema).

            ---

            # INPUT
            Teacher request: 
            {text}
        """
    def get_retrival_prompt(self, prompt: ParsedPrompt):
        return f"""
            # TASK
                You are a specialist in designing language tests. As the first agent in a large test-generation system, your task is to extract and return a list of topics that will be useful for generating the test.

                You must return the answer in the following format:
                ["topic1", "topic2", "topic3", ... "topicx"]

                You are ONLY allowed to choose from the following pool of topics:

                English tenses definitions:

                Present Simple
                Present Continuous
                Present Perfect
                Present Perfect Continuous

                Past Simple
                Past Continuous
                Past Perfect
                Past Perfect Continuous

                Future Simple
                Future Continuous
                Future Perfect
                Future Perfect Continuous

                AND
                reading, writing, vocabulary, grammar -> instructions for creating exam-style tasks

                ---

                # TEACHER REQUEST
                "{prompt.model_dump()}"

                ---

                # RULES
                You are strictly forbidden to return anything other than the list.
        
        """

    def get_generation_prompt(self, retrieval, parsed_prompt: ParsedPrompt):
        return f"""
        # ROLE
        You are an expert designer specializing in English language tests.
        You create structured, high-quality English tests based strictly on teacher input.

        ---

        # OBJECTIVE
        Generate a COMPLETE English test that strictly follows:
        - teacher instructions (highest priority)
        - provided retrieval data (supporting only)

        ---

        # HIERARCHY OF INPUTS
        1. Teacher input = ABSOLUTE PRIORITY (must always be followed)
        2. Retrieval data = inspiration only (NEVER overrides teacher input)

        If conflict occurs → ALWAYS follow teacher input.

        ---

        # HARD CONSTRAINTS (MANDATORY)
        - You MUST generate EXACTLY {parsed_prompt.total_amount} exercises 
        - Each exercise MUST contain BETWEEN 6 and 10 questions unless teacher said diffrently
        - Each exercise MUST be meaningful and non-trivial
        - You MUST include ALL topics requested in teacher input
        - Each topic MUST appear in AT LEAST one full exercise
        - YOU ALWAYS MUST skip reading, listening and writing exercises

        ---

        # TOPIC DISTRIBUTION (STRICT)
        - Distribute exercises EVENLY across topics
        - NO topic may exceed 40% of the test

        ---

        # EXERCISE DESIGN RULES
        - Each exercise must have ONE PRIMARY focus (grammar or skill)
        - NEVER mix multiple unrelated grammar topics in one exercise

        - Each question MUST be unique:
            - different sentence
            - different vocabulary
            - different context

        - STRICTLY FORBIDDEN:
            - repeating sentence structures
            - minor variations of the same sentence
            - exercise-template-type repetition

        ---

        # VARIETY REQUIREMENT
        You MUST use a mix of exercise types:
        - multiple choice
        - gap filling
        - sentence transformation
        - matching
        - error correction
        - ordering

        Avoid repeating the same format more than twice.

        # DIFFICULTY ADJUSTMENT

        If level = A2:
        - simple vocabulary
        - direct grammar usage
        - short texts

        If level = B1/B2:
        - include distractors
        - use context-based grammar
        - avoid obvious answers

        If level = C1:
        - paraphrasing
        - ambiguity allowed
        - advanced vocabulary

        ---

        # SELF-VALIDATION (MANDATORY)
        Before producing final JSON, internally verify:
        - Number of exercises == {parsed_prompt.total_amount}
        - Each exercise has 6–10 questions
        - All requested topics are covered
        - Topic distribution is balanced
        - Reading limits are respected

        If ANY condition fails → REGENERATE before output.

        ---

        - Output MUST match the schema exactly:
        {GeneratedTest.model_json_schema()}

        - YOU MUST include the ANSWER KEY as the LAST element in the "exercises" list.
        - The answer key exercise MUST have:
            "instruction": "Answer Key",
            "body": "Provide all answers here"

        ---

        # INTERNAL PLANNING STEP (HIDDEN - DO NOT OUTPUT)
        First, create an internal plan:
        - list 6 exercises
        - assign topic to each
        - assign type (MCQ, gap fill, etc.)

        Then generate the full test based on that plan.

        ---

        # INPUTS

        ## TEACHER INPUT
        {parsed_prompt}

        ## PROVIDED DATA (RAG CONTEXT)
        {retrieval}
        """

    def get_reading_prompt(self, retrieval, parsed_prompt):
        return f"""
            # ROLE
            You are an expert in designing high-quality English reading comprehension tests.

            ---

            # OBJECTIVE
            Generate reading comprehension exercises ONLY.

            ---

            # HARD CONSTRAINTS (MANDATORY)
            - Generate EXACTLY 1 or 2 reading exercises unless teacher said something else.
            - Each reading must include:
                - a text (500–700 words for B1-B2, longer for C1)
                - 5–8 comprehension questions

            ---

            # READING REQUIREMENTS
            - Text must be engaging, realistic, and coherent
            - Use varied vocabulary appropriate to level
            - Avoid artificial or repetitive phrasing

            ---

            # QUESTIONS REQUIREMENTS
            Questions must include mix of:
            - main idea
            - detail understanding
            - inference
            - vocabulary in context

            Avoid obvious answers.

            ---

            # DIFFICULTY
            (A2 / B1-B2 / C1 rules same as before)

            ---

            - Output MUST match the schema exactly:
            {GeneratedTest.model_json_schema()}

            - YOU MUST include the ANSWER KEY as the LAST element in the "exercises" list.
            - The answer key exercise MUST have:
                "instruction": "Answer Key",
                "body": "Provide all answers here"

            ---

            # IMPORTANT
            - Do NOT generate grammar exercises
            - Do NOT generate multiple unrelated texts in one exercise
            - Each exercise = one reading passage

            ---

            # INPUTS

            ## TEACHER INPUT
            {parsed_prompt}

            ## RAG DATA
            {retrieval}
        """

    def get_writing_prompt(self, retrieval, parsed_prompt):
        return f"""
            # ROLE
            You are an expert in designing high-quality English writing tasks, specialized in email and letter writing.

            ---

            # OBJECTIVE
            Generate writing exercises ONLY, specifically focusing on "writing an email" or "writing a letter" as requested.

            ---

            # HARD CONSTRAINTS (MANDATORY)
            - Generate EXACTLY 1 writing exercise unless the teacher specified a different amount.
            - The exercise must include:
                - Clear instructions/prompt for the student.
                - Context for the writing (who is the recipient, what is the purpose).
                - 3-4 specific points the student must include in their writing.
                - Word count requirement based on the level:
                    - A1-A2: 50–80 words
                    - B1: 100–120 words
                    - B2: 300–350 words
                    - C1: 400–600 words

            ---

            # WRITING REQUIREMENTS
            - The prompt must be realistic and engaging.
            - It should clearly state whether the tone should be formal or informal.
            - Use varied scenarios (e.g., inviting a friend, complaining to a store, applying for a job).

            ---

            # DIFFICULTY
            - Adjust the complexity of the scenario and the required language functions based on the level ({parsed_prompt.level}).

            ---

            # OUTPUT FORMAT
            - Output MUST match the schema exactly:
            {GeneratedTest.model_json_schema()}

            - YOU MUST include a MODEL ANSWER as the LAST element in the "exercises" list.
            - The model answer exercise MUST have:
                "instruction": "Answer Key",
                "body": "Provide a high-quality model answer here that meets all the criteria."

            ---

            # IMPORTANT
            - Do NOT generate grammar or reading exercises.
            - Focus solely on the writing task and its requirements.

            ---

            # INPUTS

            ## TEACHER INPUT
            {parsed_prompt}

            ## RAG DATA
            {retrieval}
        """

    def get_test_restructuring_prompt(self, test_data: GeneratedTest):
        return f"""
            # ROLE
            You are an expert in structuring language tests for PDF generation.
            Your task is to take a raw GeneratedTest (which has simple instruction and body strings) and restructure it into a highly structured PDFTest format.

            ---

            # INPUT RAW DATA
            {test_data.model_dump_json()}

            ---

            # TARGET SCHEMA
            Your output must be a valid JSON object matching this schema:
            {PDFTest.model_json_schema()}

            ---

            # STRUCTURE GUIDELINES (task_type mapping)

            1. "multiple_choice": 
               - Body contains questions with options like A., B., C.
               - Separate them into 'questions' list where each has 'question', 'options', and optional 'answer'.

            2. "matching":
               - Body contains two columns or lists to be matched (e.g. 1-5 and A-E).
               - Map to 'left_column' and 'right_column'.

            3. "true_false":
               - Body contains statements to be marked T/F.
               - Map to 'statements' list.

            4. "word_formation":
               - Body contains sentences with gaps and a base word in brackets or at the end.
               - Map to 'items' list with 'sentence_with_gap' and 'root_word'.

            5. "gap_fill":
               - Body has a text with gaps like [ 1 ] and a list of sentences/words to insert at the bottom.
               - Map to 'passage' and 'choices'.

            6. "transformation":
               - Body contains: Original sentence, a Key word, and a sentence with a gap.
               - Map to 'items' list with 'original_sentence', 'key_word', and 'sentence_with_gap'.

            7. "writing":
               - Body is a writing prompt/instructions.
               - Map to 'prompt' and 'word_count_range'.

            8. "cloze":
               - Body is a text with gaps like ___1___ and a list of options for each gap below.
               - Map to 'passage' and 'options_per_gap'.

            9. "simple_text":
               - Use this for "Answer Key" or any other unstructured text.

            ---

            # CRITICAL RULES
            - Return ONLY valid JSON.
            - Do NOT add any conversational text or markdown (No ```json).
            - Be extremely precise when splitting strings into structured fields.
            - Ensure the 'task_type' field is present and correct for every exercise.
        """

    def get_test_checking_prompt(self, test, parsed_prompt):
        return f"""
        You are a strict Test Quality Validator AND Fixer.

        Your task is to analyze the generated test and IMPROVE it so that it fully meets the requirements.

        === INPUT DATA ===
        TEST (JSON):
        {test}

        TEACHERS REQUIREMENTS (parsed_prompt):
        {parsed_prompt}

        === YOUR TASK ===

        1. DUPLICATION CHECK
        - If any tasks/questions are repeated or very similar:
        - You MUST rewrite them to be clearly different.
        - Keep the same difficulty level.

        2. DIVERSITY CHECK
        - Ensure tasks are diverse:
        - different grammar types
        - different skills (reading, writing, use of English)
        - different instructions
        - If the user explicitly requested repetition → respect it.

        3. REQUIREMENTS MATCH
        - Ensure the test strictly follows parsed_prompt:
        - number of tasks
        - task types
        - difficulty level
        - age group
        - If something is wrong → FIX IT.

        4. QUALITY CHECK
        - Improve unclear instructions.
        - Make tasks meaningful and non-trivial.
        - Ensure the test is usable by a teacher.

        === OUTPUT FORMAT ===

        - Return EXACTLY the same JSON structure as in TEST.
        - DO NOT add new fields.
        - DO NOT remove fields.
        - ONLY modify values where necessary to fix issues.
        - Return ONLY valid JSON.
        - Do NOT add any conversational text or markdown (No ```json).
        - Be extremely precise when splitting strings into structured fields.
        - Ensure the 'task_type' field is present and correct for every exercise.
        - You ABSOLUTELY MUST RETURN WHOLE TEST DO NOT MISS ANYTHING

        === CRITICAL RULES ===
        - Return ONLY valid JSON.
        - No markdown, no comments, no explanations.
        - Preserve all keys (especially 'task_type').
        - Ensure all fields are properly filled.
        - Ensure consistency across the whole test.

        === IMPORTANT ===
        - If the test is already correct → return it unchanged.
        - Otherwise → return FULLY FIXED version.
    """

    def clean_json_response(self, response: str) -> str:
        """
        Cleans the AI response by removing markdown code blocks and extra text.
        """
        import re
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

    

