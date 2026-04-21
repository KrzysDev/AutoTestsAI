from backend.app.models.schemas import ParsedPrompt, PromptTestSection, GeneratedTest, Exercise, PDFTest, Form
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

    def get_combined_generation_prompt(self, retrieval, reading_data, writing_data, parsed_prompt: Union[ParsedPrompt, Form], reading_enabled: bool, writing_enabled: bool):
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

    def get_combined_html_generation_prompt(self, retrieval, reading_data, writing_data, parsed_prompt: Union[ParsedPrompt, Form], reading_enabled: bool, writing_enabled: bool):
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

# VISUAL DESIGN (professional printed English exam style)

Typography:
- Body: Georgia, 'Times New Roman', serif — 11pt
- Headers/labels: 'Segoe UI', Tahoma, sans-serif
- Questions: 10.5pt, line-height:1.7 | Exercise titles: 12pt bold uppercase | h1: 18pt bold uppercase, letter-spacing:3px

Colors: primary=#1a2744 | accent=#c0392b | light-gray=#f5f5f5 | white=#fff | muted=#666

Header: full-width #1a2744 bar, white text, title centered uppercase. Below: Level | Age Group | Total Score. Bottom border: 4px solid #c0392b.
Student info: 3-col table layout, label+dotted underline (border-bottom:1.5px dotted #333), bg #f5f5f5, padding 10px.
Exercise blocks: white bg, border:1.5px solid #ddd, padding:16px, margin-bottom:20px, page-break-inside:avoid. Number tag: #c0392b bg, white text, 9pt, float:right. Score: italic gray float:right "( X pts )". Title: bold uppercase #1a2744, border-left:4px solid #c0392b, padding-left:8px. Instructions: italic #666 10pt. Questions: numbered, 10.5pt, margin-bottom:8px. Answer lines: border-bottom:1px solid #aaa, inline-block, min-width:200px.
Section dividers: #1a2744 bg, white text, center, padding 8px, uppercase, letter-spacing:2px, 10pt.
MCQ options: A) B) C) format, styled circle spans.
Gap fill: underscores, min-width 120px, border-bottom.
Reading passage: #f5f5f5 bg, border-left:4px solid #1a2744, padding 15px, bold heading above.
Writing box: border:1.5px solid #aaa, width:100%, min-height:200px, white bg, repeating-linear-gradient for lined paper.
Answer Key: page-break-before:always, #1a2744 header "ANSWER KEY — FOR TEACHER USE ONLY", 4px solid #c0392b accent strip, 3-col table, exercise boxes: border 1px solid #444, padding 10px, bg #1e3055, white text.

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

    def get_test_checking_prompt(self, test: GeneratedTest, parsed_prompt: Union[ParsedPrompt, Form]):
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
        
        Rules:
            - if the teacher is asking about test generation, his message is probably not specified enough. If that is so ask for missing data. The following generating prompt must contain:
                -THERE MUST BE A CEFR LEVEL SPECIFIED (A1, A2, B1, B2, C1, C2)
                -THERE MUST BE target age group (kids, teens or adults?)
                -THERE MUST BE total_amount (how many exercises teacher wants to have on exam)
                - if THERE IS NOT probably such data provided so ask teacher to clarify.

        question : {prompt}
        
        
        """
