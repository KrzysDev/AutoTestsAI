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
    - total_amount: total exercises count
    If any field is unclear → make a reasonable assumption, do NOT return "general".

    If NO (purely general question, no test creation intent) → return ONLY the word: general

    Message: {text}"""


    def get_retrival_prompt(self, prompt: ParsedPrompt):
        return f"""Return a JSON list of topics needed to generate this test. Choose ONLY from the list below. Return ONLY the list — no other text.

        Allowed topics:
        Present Simple, Present Continuous, Present Perfect, Present Perfect Continuous,
        Past Simple, Past Continuous, Past Perfect, Past Perfect Continuous,
        Future Simple, Future Continuous, Future Perfect, Future Perfect Continuous,
        reading, writing, vocabulary, grammar

        Teacher request: {prompt.model_dump()}"""

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

    def get_reading_prompt(self, retrieval, parsed_prompt):
        return f"""Generate reading comprehension exercises ONLY. Return ONLY valid JSON, no markdown.

Rules:
- Generate 1–2 reading exercises (unless teacher specified otherwise)
- Each exercise: a text (500–700 words for B1-B2, longer for C1) + 5–8 comprehension questions
- Questions must mix: main idea, detail, inference, vocabulary in context
- No grammar exercises; one passage per exercise

Difficulty same as standard levels (A2/B1-B2/C1).

Output schema: {GeneratedTest.model_json_schema()}
Last exercise MUST be: {{"instruction": "Answer Key", "body": "..."}}

Teacher input: {parsed_prompt}
RAG context: {retrieval}"""

    def get_writing_prompt(self, retrieval, parsed_prompt):
        return f"""Generate writing exercises ONLY (email or letter writing). Return ONLY valid JSON, no markdown.

Rules:
- Generate 1 exercise (unless teacher specified otherwise)
- Include: clear instructions, context (recipient + purpose), 3–4 bullet points to address, word count:
  A1-A2: 50–80 | B1: 100–120 | B2: 300–350 | C1: 400–600
- Prompt must be realistic, state formal/informal tone clearly
- No grammar or reading exercises

Level: {parsed_prompt.level}

Output schema: {GeneratedTest.model_json_schema()}
Last exercise MUST be a model answer: {{"instruction": "Answer Key", "body": "..."}}

Teacher input: {parsed_prompt}
RAG context: {retrieval}"""

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
