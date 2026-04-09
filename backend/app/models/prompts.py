
from backend.app.models.schemas import ParsedPrompt, TestSection

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
            

            {TestSection.model_json_schema()}

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