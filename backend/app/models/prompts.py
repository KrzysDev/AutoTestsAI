from backend.app.models.schemas import ParsedPrompt, PromptTestSection, GeneratedTest, Exercise, PDFTest
import json

# <summary>
# System prompts used by agentic system to generate tests.
# </summary>
class SystemPrompts:
    def __init__(self):
        pass

    def get_classification_prompts(self, text: str):
        return f"""You are processing a teacher's message. 

    FIRST: Does the message express intent to CREATE a test or exam?
    Intent = any of: create, make, generate, write, prepare, give me, build + test, exam, quiz, classwork, worksheet.

    If YES → extract parameters and return ONLY this JSON (no markdown, no extra text):
    {ParsedPrompt.model_json_schema()}

    Field rules:
    - task: teacher's original request verbatim
    - level: CEFR only — A1, A2, B1, B2, C1, C2
    - age_group: one of — kids, teens, adults
    - sections: list where task_type is one of — vocabulary, grammar, reading, writing; amount = number of such sections
    - subject (in test section) - one of the given: 
            "Present Simple",
            "Present Continuous",
            "Present Perfect",
            "Present Perfect Continuous",
            "Past Simple",
            "Past Continuous",
            "Past Perfect",
            "Past Perfect Continuous",
            "Future Simple",
            "Future Continuous",
            "Future Perfect",
            "Future Perfect Continuous"
    - total_amount: total exercises count
    - exercises amount MUST be equal to total amount of exercises. Example: if total_amount = 20 then, sum of sections.amounts MUST BE EQUAL 20
    If any field is unclear → make a reasonable assumption, do NOT return "general".

    If NO (purely general question, no test creation intent) → return ONLY the word: general

    Message: {text}"""


    def get_generation_prompt(self, retrieval, parsed_prompt: ParsedPrompt):
        return f"""You are an expert English test designer. Generate a complete English test.

        PRIORITY: Teacher input overrides everything. RAG data is inspiration only.

        MANDATORY RULES:
        - Generate EXACTLY {parsed_prompt.total_amount} exercises
        - Each exercise: 6–10 questions (unless teacher specified otherwise)
        - Cover ALL teacher-requested topics; each topic in at least one exercise
        - Skip reading, listening, and writing exercises
        - Distribute topics evenly; no topic exceeds 40% of the test
        - Each exercise has ONE primary grammar/skill focus
        - All questions must be unique (different sentence, vocabulary, context)
        - Use varied formats: multiple choice, gap fill, transformation, matching, error correction, ordering — no format repeated more than twice

        Difficulty:
        - A2: simple vocab, direct grammar, short texts
        - B1/B2: distractors, context-based grammar
        - C1: paraphrasing, ambiguity, advanced vocab

        Output schema (return ONLY valid JSON, no markdown):
        {GeneratedTest.model_json_schema()}

        The LAST exercise MUST be the Answer Key: {{"instruction": "Answer Key", "body": "..."}}

        Teacher input: {parsed_prompt}
        RAG context: {retrieval}"""

    def get_combined_generation_prompt(self, retrieval, reading_data, writing_data, parsed_prompt: ParsedPrompt, reading_enabled: bool, writing_enabled: bool):
        # Count how many sections are grammar/vocabulary (non-reading, non-writing)
        grammar_vocab_sections = [s for s in parsed_prompt.sections if s.task_type not in ("reading", "writing")]
        reading_sections = [s for s in parsed_prompt.sections if s.task_type == "reading"]
        writing_sections = [s for s in parsed_prompt.sections if s.task_type == "writing"]

        grammar_vocab_amount = sum(s.amount for s in grammar_vocab_sections)
        reading_amount = sum(s.amount for s in reading_sections) if reading_enabled else 0
        writing_amount = sum(s.amount for s in writing_sections) if writing_enabled else 0

        # Build the reading section block
        reading_block = ""
        if reading_enabled:
            reading_block = f"""
        ═══════════════════════════════════════════════════════════════
        SECTION B: READING COMPREHENSION EXERCISES
        ═══════════════════════════════════════════════════════════════

        YOU MUST generate reading comprehension exercises as part of this test. This is NOT optional. FAILURE TO INCLUDE READING EXERCISES WILL RESULT IN IMMEDIATE REJECTION OF YOUR ENTIRE OUTPUT.

        READING EXERCISE MANDATORY RULES — YOU ABSOLUTELY HAVE TO FOLLOW EVERY SINGLE ONE:
        - YOU MUST generate 1–2 reading exercises (unless the teacher explicitly specified a different number)
        - Each reading exercise MUST contain: a coherent, well-written passage (500–700 words for B1-B2, longer for C1) PLUS 5–8 comprehension questions
        - The comprehension questions MUST be a mix of: main idea questions, detail questions, inference questions, and vocabulary-in-context questions
        - YOU ARE STRICTLY FORBIDDEN FROM generating any grammar exercises in this section — ONLY reading comprehension
        - Each exercise MUST contain exactly ONE passage — YOU MUST NOT split a passage across multiple exercises
        - The passage MUST be original, coherent, multi-paragraph text — NOT a collection of random sentences
        - Questions MUST use paraphrasing — YOU ARE FORBIDDEN FROM copying exact phrases from the passage into correct answer options
        - YOU MUST create plausible but incorrect distractors for multiple choice questions
        - YOU MUST include subtle semantic differences in answer options
        - YOU MUST balance difficulty across questions

        READING DIFFICULTY CALIBRATION — YOU MUST FOLLOW THESE EXACTLY:
        - A2: simple vocabulary, short texts (300-400 words), direct comprehension questions, straightforward language
        - B1/B2: moderate vocabulary, texts 500-700 words, context-based questions with distractors, paraphrased answers
        - C1: advanced vocabulary, texts 700+ words, inference-heavy questions, ambiguity in answer options, nuanced comprehension

        READING RAG CONTEXT (use as inspiration ONLY — teacher input ALWAYS overrides):
        {reading_data}
        """

                # Build the writing section block
        writing_block = ""
        if writing_enabled:
            writing_block = f"""
        ═══════════════════════════════════════════════════════════════
        SECTION C: WRITING EXERCISES
        ═══════════════════════════════════════════════════════════════

        YOU MUST generate writing exercises as part of this test. This is NOT optional. FAILURE TO INCLUDE WRITING EXERCISES WILL RESULT IN IMMEDIATE REJECTION OF YOUR ENTIRE OUTPUT.

        WRITING EXERCISE MANDATORY RULES — YOU ABSOLUTELY HAVE TO FOLLOW EVERY SINGLE ONE:
        - YOU MUST generate 1 writing exercise (unless the teacher explicitly specified a different number)
        - The writing exercise types MUST be one of: email writing, letter writing, or matching headings
        - Each writing exercise MUST include: clear instructions, context (recipient + purpose), 3–4 bullet points that the student must address, and a word count requirement
        - The word count requirements MUST follow these EXACT ranges based on level — YOU ARE FORBIDDEN FROM DEVIATING:
        A1-A2: 50–80 words
        B1: 100–120 words
        B2: 300–350 words
        C1: 400–600 words
        - The writing prompt MUST be realistic and clearly state whether the tone should be formal or informal
        - YOU ARE STRICTLY FORBIDDEN FROM generating any grammar or reading exercises in this section — ONLY writing exercises
        - YOU MUST define a clear audience and purpose for the writing task
        - YOU MUST match the tone to the context (formal/informal)
        - YOU MUST include all required bullet points that the student needs to address
        - YOU MUST ensure a natural opening and closing is expected
        - YOU ARE FORBIDDEN FROM mixing registers within a single writing task

        CURRENT LEVEL FOR WRITING: {parsed_prompt.level}

        WRITING RAG CONTEXT (use as inspiration ONLY — teacher input ALWAYS overrides):
        {writing_data}
        """

                # Build the combined prompt
        combined_prompt = f"""YOU ARE AN EXPERT ENGLISH TEST DESIGNER. YOU MUST GENERATE A COMPLETE, UNIFIED ENGLISH TEST IN A SINGLE OUTPUT.

        THIS IS A SINGLE, ATOMIC OPERATION. YOU MUST PRODUCE THE ENTIRE TEST — INCLUDING ALL GRAMMAR/VOCABULARY EXERCISES{', READING COMPREHENSION EXERCISES' if reading_enabled else ''}{', AND WRITING EXERCISES' if writing_enabled else ''} — IN ONE SINGLE JSON RESPONSE. YOU ARE STRICTLY FORBIDDEN FROM PRODUCING PARTIAL OUTPUT.

        ═══════════════════════════════════════════════════════════════
        ABSOLUTE PRIORITY HIERARCHY — OBEY THIS WITHOUT EXCEPTION:
        ═══════════════════════════════════════════════════════════════
        1. Teacher input OVERRIDES everything — it is the supreme authority
        2. RAG data is inspiration ONLY — it MUST NOT override teacher instructions
        3. These rules are MANDATORY — you MUST follow every single one

        ═══════════════════════════════════════════════════════════════
        SECTION A: GRAMMAR AND VOCABULARY EXERCISES
        ═══════════════════════════════════════════════════════════════

        YOU MUST generate grammar and vocabulary exercises as the CORE of this test. This is NOT optional.

        GRAMMAR/VOCABULARY MANDATORY RULES — YOU ABSOLUTELY HAVE TO FOLLOW EVERY SINGLE ONE:
        - YOU MUST generate EXACTLY {grammar_vocab_amount} grammar/vocabulary exercises
        - Each exercise MUST contain 6–10 questions (unless the teacher explicitly specified otherwise)
        - YOU MUST cover ALL teacher-requested topics; each topic MUST appear in at least one exercise
        - YOU ARE STRICTLY FORBIDDEN FROM generating reading, listening, or writing exercises in this section
        - YOU MUST distribute topics evenly — no single topic is allowed to exceed 40% of the grammar/vocabulary section
        - Each exercise MUST have ONE primary grammar or skill focus — YOU ARE FORBIDDEN FROM mixing multiple grammar topics in a single exercise
        - ALL questions MUST be unique — every single question MUST have a different sentence, different vocabulary, and different context. YOU ARE ABSOLUTELY FORBIDDEN FROM creating duplicate or near-duplicate questions
        - YOU MUST use varied exercise formats: multiple choice, gap fill, transformation, matching, error correction, ordering — NO format is allowed to be repeated more than twice across the entire grammar/vocabulary section

        GRAMMAR/VOCABULARY DIFFICULTY CALIBRATION — YOU MUST FOLLOW THESE EXACTLY:
        - A2: simple vocabulary, direct grammar application, short and clear sentences
        - B1/B2: distractors that test understanding, context-based grammar application, moderate complexity
        - C1: paraphrasing, grammatical ambiguity, advanced vocabulary, complex sentence structures
        {reading_block}{writing_block}
        ═══════════════════════════════════════════════════════════════
        FINAL EXERCISE: ANSWER KEY — THIS IS MANDATORY
        ═══════════════════════════════════════════════════════════════

        THE VERY LAST EXERCISE IN YOUR OUTPUT MUST BE THE ANSWER KEY.
        IT MUST have this exact format: {{"instruction": "Answer Key", "body": "..."}}
        The body MUST contain correct answers for ALL exercises in the test — grammar/vocabulary{', reading' if reading_enabled else ''}{', and writing (model answer)' if writing_enabled else ''}.
        YOU ARE STRICTLY FORBIDDEN FROM omitting the Answer Key.
        {f'For writing exercises, the Answer Key MUST contain a complete model answer — not just notes or bullet points. The model answer MUST follow the exact word count range specified for the level.' if writing_enabled else ''}

        ═══════════════════════════════════════════════════════════════
        OUTPUT FORMAT — OBEY EXACTLY OR YOUR OUTPUT WILL BE REJECTED
        ═══════════════════════════════════════════════════════════════

        YOU MUST return ONLY valid JSON. NO markdown. NO code fences. NO extra text before or after the JSON.
        YOU MUST follow this EXACT schema — any deviation WILL result in rejection:
        {GeneratedTest.model_json_schema()}

        THE EXERCISES ARRAY MUST CONTAIN ALL EXERCISES IN THIS ORDER:
        1. Grammar/vocabulary exercises (EXACTLY {grammar_vocab_amount} exercises)
        {f'2. Reading comprehension exercises (1-2 exercises)' if reading_enabled else ''}
        {f'3. Writing exercises (1 exercise)' if writing_enabled else ''}
        {"4" if writing_enabled else "3" if reading_enabled else "2"}. Answer Key (EXACTLY 1 exercise, ALWAYS last)

        TOTAL EXERCISE COUNT IN THE EXERCISES ARRAY: {grammar_vocab_amount}{f' + reading exercises' if reading_enabled else ''}{f' + writing exercises' if writing_enabled else ''} + 1 (Answer Key)

        ═══════════════════════════════════════════════════════════════
        INPUT DATA
        ═══════════════════════════════════════════════════════════════

        Teacher input (THIS IS YOUR PRIMARY SOURCE OF TRUTH): {parsed_prompt}
        Grammar/Vocabulary RAG context (inspiration only): {retrieval}"""

        return combined_prompt

    def get_test_restructuring_prompt(self, test_data: GeneratedTest):
        return f"""Restructure the raw GeneratedTest into PDFTest format. Return ONLY valid JSON, no markdown.

        task_type mapping:
        - multiple_choice: questions with A/B/C options → list of {{question, options, answer?}}
        - matching: two columns to match → {{left_column, right_column}}
        - true_false: T/F statements → {{statements}}
        - word_formation: gaps + base word → {{items: [{{sentence_with_gap, root_word}}]}}
        - gap_fill: text with [1] gaps + word bank → {{passage, choices}}
        - transformation: original + key word + gapped sentence → {{items: [{{original_sentence, key_word, sentence_with_gap}}]}}
        - writing: prompt + word count → {{prompt, word_count_range}}
        - cloze: text with ___1___ gaps + options per gap → {{passage, options_per_gap}}
        - simple_text: Answer Key or unstructured content

        Target schema: {PDFTest.model_json_schema()}

        Input: {test_data.model_dump_json()}"""

    def get_test_checking_prompt(self, test: GeneratedTest, parsed_prompt: ParsedPrompt):
        return f"""You are a Test Validator and Fixer. Analyze the test and fix any issues. Return ONLY the corrected test as valid JSON — no markdown, no extra text.

        Fix if needed:
        1. Duplicated/similar questions → rewrite to be clearly different, same difficulty
        2. Low diversity → ensure varied formats (gap fill, transformation, MCQ, error correction, matching)
        3. Mismatch with requirements → fix number of tasks, types, difficulty, age group
        4. Unclear instructions → improve them

        Rules:
        - Same JSON schema as input (no new/removed fields)
        - Every exercise must have: instruction, body, task_type
        - Return the FULL test — do not truncate
        - If test is already correct → return it unchanged

        Test: {test.model_dump_json(indent=2)}
        Requirements: {parsed_prompt.model_dump_json(indent=2)}"""

    def get_test_fixing_prompt(self, test: GeneratedTest, teacher_prompt: str):
            return f"""Modify the English test according to the teacher's instructions. Return ONLY valid JSON, no markdown.

        Rules:
        - Apply all teacher-requested changes
        - Maintain original JSON schema and quality/difficulty (unless teacher changed it)
        - Every exercise must have: instruction, body
        - Return the FULL test — do not truncate
        - If instructions are unclear, interpret in the way that best improves the test

        Test: {test.model_dump_json(indent=2)}
        Teacher instructions: "{teacher_prompt}"""

    def clean_json_response(self, response: str) -> str:
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            return json_match.group(1).strip()
        start_idx = response.find('{')
        if start_idx == -1:
            start_idx = response.find('[')
        end_idx = response.rfind('}')
        if end_idx == -1:
            end_idx = response.rfind(']')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return response[start_idx:end_idx + 1].strip()
        return response.strip()

    def get_general_question_prompt(self, prompt: str):
        return f""" 
        You are a test designer assistant. You can generate english tests on various topics in various styles.
        Your task is to respond to user general question.

        Do not answer any questions not related with your task. You are a english test designer. Remember that.

        Answer very shortly, do not talk to much. Direct answers only.
        
        Always answer in user language.

        question : {prompt}
        
        
        """
