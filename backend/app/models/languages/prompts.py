from backend.app.models.languages.schemas import ParsedPrompt, PromptTestSection, Form
from typing import Union
import json

# <summary>
# System prompts used by agentic system to generate tests.
# </summary>
class SystemPrompts:
    def __init__(self):
        pass

    def get_classification_prompts(self, text: str):
        return f"""
            You are a classifier.

            Your task is to classify the user's message into ONE of two labels:

            * "general" → casual conversation, questions, or anything NOT asking to create a test
            * "request" → user wants to create/generate/make an English test or exam

            ---

            Examples:

            Message: "Hi, how are you?"
            Answer: general

            Message: "Explain present perfect"
            Answer: general

            Message: "Create a B2 English test about travel"
            Answer: request

            Message: "Generate exam with grammar and reading tasks"
            Answer: request

            Message: "Make a test for teenagers"
            Answer: request

            ---

            Rules:

            * Output ONLY one word: general OR request
            * No explanations
            * No extra text
            * you can only generate english exercises. If teacher demands something diffrent than english output general.

            ---

            Message:
            {text}

        
        """

    def get_parsing_prompt(self, text: str):
        return f"""
        You are processing a teacher's request for test generation. You have to iterate through it and extract all necessary data, then return it in provided format.

        #PROVIDED FORMAT
        {json.dumps(ParsedPrompt.model_json_schema(), indent=2)}

        #RULES
         - you MUST ALWAYS return ANSWER IN PROVIDED FORMAT. Never return answer diffrently 
         - you must ALWAYS return valid json. No mistakes, no markdown sighns like ``` or ```json
         - YOU MUST return ONLY valid JSON. NO markdown. NO code fences. NO extra text before or after the JSON.
         - YOU MUST follow this EXACT schema — any deviation WILL result in rejection
        
        #IMPORTANT INFORMATION
        1.Sections in provided format look like this:
            {json.dumps(PromptTestSection.model_json_schema(), indent=2)}

        2. They represent sections of a test. Possible values:
                task_type: Literal["vocabulary", "grammar", "reading", "writing"]
                description: string -> description of how exercise has to be created (implementation plan). Its either teachers idea or yours if teacher did not give enough information.
                subject: Literal[
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
                ]
                visuals: string -> description of how exercise has to look visually.
                amount : int
        
        #Teacher's request:
        {text}

        """

    def get_combined_html_generation_prompt(self, retrieval, reading_data, writing_data, parsed_prompt: Union[ParsedPrompt, Form, str], reading_enabled: bool, writing_enabled: bool):
        grammar_vocab_sections = [s for s in parsed_prompt.sections if s.task_type not in ("reading", "writing")]
        grammar_vocab_amount = sum(s.amount for s in grammar_vocab_sections)

        reading_block = ""
        if reading_enabled:
            rag_line = f"\nReading RAG context (inspiration only): {reading_data}" if reading_data else ""
            reading_block = f"""
## SECTION B: READING COMPREHENSION (mandatory)
- Generate 1–2 reading exercises
- Each: coherent original multi-paragraph passage + 5–8 comprehension questions
- Question types: main idea, detail, inference, vocabulary-in-context
- No grammar exercises in this section
- Paraphrase in questions — never copy exact phrases from passage into answers
- Create plausible incorrect distractors for MCQ
- Passage length by level: A2: 300-400w | B1/B2: 500-700w | C1: 700+w{rag_line}
"""

        writing_block = ""
        if writing_enabled:
            rag_line = f"\nWriting RAG context (inspiration only): {writing_data}" if writing_data else ""
            writing_block = f"""
## SECTION C: WRITING (mandatory)
- Generate 1 writing exercise (email, letter, or essay)
- Include: clear instructions, context (recipient+purpose), 3–4 bullet points, word count requirement
- Word count: A1-A2: 50–80w | B1: 100–120w | B2: 300–350w | C1: 400–600w
- State formal/informal tone clearly
- Render writing box as bordered box (min-height: 200px)
- Level: {parsed_prompt.level}{rag_line}
"""

        rag_grammar_line = f"\nGrammar/Vocabulary RAG context (inspiration only): {retrieval}" if retrieval else ""

        # Build numbered structure list
        structure_items = [
            "1. Header bar (title, level, age group, total score)",
            "2. Student info bar (Name / Date / Class)",
            '3. Section divider: "SECTION A — GRAMMAR & VOCABULARY"',
            f"4. Grammar/vocabulary exercises (exactly {grammar_vocab_amount})",
        ]
        step = 5
        if reading_enabled:
            structure_items.append(f'{step}. Section divider: "SECTION B — READING COMPREHENSION"')
            step += 1
            structure_items.append(f'{step}. Reading exercises')
            step += 1
        if writing_enabled:
            structure_items.append(f'{step}. Section divider: "SECTION C — WRITING"')
            step += 1
            structure_items.append(f'{step}. Writing exercise')
            step += 1
        structure_items.append(f"{step}. Answer Key (always last, page-break-before: always)")
        structure_block = "\n".join(structure_items)

        combined_prompt = f"""You are an expert English test designer and web designer. Generate a complete, print-ready HTML test file.

# ABSOLUTE RULES (violation = rejection)
1. Output ONLY raw HTML starting with <!DOCTYPE html>. No markdown, no code fences, no explanations.
2. CSS+HTML only — zero JavaScript.
3. Teacher input overrides everything. RAG data is inspiration only.
4. Must be convertible to PDF via WeasyPrint.

# WEASYPRINT CSS
Required @page rule:
@page {{ size: A4; margin: 1.5cm 2cm; @bottom-center {{ content: "— " counter(page) " —"; font-size: 9pt; color: #999; }} }}

Required reset:
* {{ box-sizing: border-box; }} body {{ margin:0; padding:0; background:#fff; }} .test-container {{ width:100%; }}

FORBIDDEN CSS (breaks WeasyPrint): display:flex, display:grid, vw/vh units, max-width on .test-container, JS-dependent CSS.
USE INSTEAD: display:table/table-cell for multi-column layouts. Use %, cm, pt, px for widths.

Page break rules:
- .answer-key-section: page-break-before: always (ONLY element with this)
- .exercise: page-break-inside: avoid
- .section-divider: page-break-before:auto; page-break-after:avoid; page-break-inside:avoid
- .exercise-title: page-break-after: avoid
- Never use page-break-before:always except on .answer-key-section
- Never use page-break-after:always anywhere

# VISUAL DESIGN
You have full creative freedom over colors, fonts, and aesthetic style. Design a professional, visually appealing printed exam. Choose a coherent color palette, readable fonts, and a polished look that fits the teacher's request.

Mandatory structural rules (layout — do NOT deviate):
- Body font-size: 10–12pt, line-height ≥ 1.5 for readability
- Header: full-width bar with test title centered, below it: Level | Age Group | Total Score
- Student info: 3-col layout using display:table/table-cell, label + underline for each field, padding ≥ 8px
- Exercise blocks: padding ≥ 12px, margin-bottom ≥ 15px, page-break-inside:avoid. Must show score "( X pts )" and exercise number
- Section dividers: full-width bar, centered uppercase text, must have page-break CSS from rules above
- MCQ options: A) B) C) format
- Gap fill blanks: border-bottom underline, min-width ≥ 100px
- Reading passage: visually distinct container (e.g. background or border), padding ≥ 12px
- Writing box: bordered, width:100%, min-height:200px
- Answer Key: page-break-before:always, answers in multi-column table layout (display:table), clearly labeled per exercise

# CONTENT STRUCTURE (follow this exact order)
{structure_block}

# SCORING
- Every exercise shows score: "( X pts )" float right
- Sum of scores = total score in header
- Grammar/vocab: 1pt/question | Reading: 2pts/question | Writing: 15pts flat
- Sequential numbering: Ex. 1, 2, 3… never skip or reset

# GRAMMAR & VOCABULARY EXERCISES (Section A)
- Exactly {grammar_vocab_amount} exercises, each 6–10 questions, one grammar focus, unique sentences
- Formats: multiple choice, gap fill, error correction, transformation, ordering, matching — no format repeated 3+ times
- Contexts relevant to age group
- Difficulty: {parsed_prompt.level}
{reading_block}{writing_block}
# INPUT DATA
Teacher input (primary source of truth): {parsed_prompt}{rag_grammar_line}"""

        return combined_prompt

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
        
        Rules:
            - if the teacher is asking about test generation, his message is probably not specified enough. If that is so ask for missing data. The following generating prompt must contain:
                -THERE MUST BE A CEFR LEVEL SPECIFIED (A1, A2, B1, B2, C1, C2)
                -THERE MUST BE target age group (kids, teens or adults?)
                -THERE MUST BE total_amount (how many exercises teacher wants to have on exam)
                -Tell teacher what information is missing.
                - if THERE IS NOT probably such data provided so ask teacher to clarify.
            - if he is requesting something diffrent than english, tell him that you only generate english exercises.

        question : {prompt}
        
        
        """

