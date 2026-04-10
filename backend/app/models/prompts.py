from backend.app.models.schemas import ParsedPrompt, PromptTestSection, GeneratedTest, Exercise

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

    def get_generation_prompt(self, retrieval, parsed_prompt):
        return f"""
            # ROLE
            You are an expert designer specializing in English language tests. 
            You create structured English tests based strictly on teacher input and provided retrieval data.

            ---

            # OBJECTIVE
            Generate a complete English test based on:
            - teacher instructions (highest priority)
            - provided retrieval data (supporting material)

            You must strictly follow all constraints and output format.

            ---

            # HIERARCHY OF INPUTS
            1. Teacher input = STRICT PRIORITY (must always be followed)
            2. Retrieval data = supporting inspiration only (never overrides teacher input)

            If there is a conflict, ALWAYS follow teacher input.

            ---

            # CORE RULES
            - Each exercise must focus on ONLY ONE grammar/topic (no mixing topics in a single task)
            Example: Present Simple exercise must NOT include Present Continuous
            - If multiple grammar points are provided, ALL must be included in the test
            - Do NOT repeat identical task templates within the same test unless absolutely necessary
            - Be creative and vary exercise formats (e.g., MCQ, matching, transformation, ordering, error correction)
            - Keep difficulty appropriate to the implied level in teacher input 
            - each exercise should have at least 5 subsections unless teacher said diffrently


            ---

            # OUTPUT REQUIREMENTS (STRICT)
            - Output MUST be valid JSON only
            - Do NOT include any explanations, markdown, or text outside JSON
            - Do NOT wrap output in ``` or any formatting
            - Output MUST match the schema of:
            {GeneratedTest.model_json_schema()}

            ---

            # TEST STRUCTURE GUIDELINES
            Your generated test should:
            - Include a defined number of exercises (4–10 depending on input complexity)
            - Cover all required grammar/topics from teacher input
            - Include different task types across the test
            - Include an answer key for all tasks


            #HOW DIFFICULT EACH EXERCISE SHOULD BE
            If level = A2:
                - use simple vocabulary
                - use direct grammar gaps
                - avoid ambiguity
                - if reading = short

                If level = B1 or B2:
                - include distractors (wrong but plausible answers)
                - mix similar tenses within context
                - use contextual reasoning instead of isolated grammar
                - avoid obvious verb cues that reveal the answer
                - readings at least 500 words or longer

                If level = C1:
                - include everything from B1/B2 rules
                - add inference-based questions
                - introduce ambiguity where appropriate (multiple plausible interpretations)
                - use paraphrasing tasks and rewording challenges

            # ANSWER KEY RULE
            - Provide a complete answer key for ALL exercises
            - Must match generated tasks exactly
            - No extra explanations in answer key
            - answer key should follow the same json schema as regular test. But use one object only. it should be something like this:
                {{
                    "instructions" : "answer key" 
                    "body" : "here you write answers"
                }}

            ---

            # INPUTS

            ## TEACHER INPUT
            {parsed_prompt}

            ## PROVIDED DATA (RAG CONTEXT)
            {retrieval}

        """

