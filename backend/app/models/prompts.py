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
        reading_sections = [s for s in parsed_prompt.sections if s.task_type == "reading"]
        writing_sections = [s for s in parsed_prompt.sections if s.task_type == "writing"]

        grammar_vocab_amount = sum(s.amount for s in grammar_vocab_sections)
        reading_amount = sum(s.amount for s in reading_sections) if reading_enabled else 0
        writing_amount = sum(s.amount for s in writing_sections) if writing_enabled else 0

        reading_block = ""
        if reading_enabled:
            reading_block = f"""
        ═══════════════════════════════════════════════════════════════
        SECTION B: READING COMPREHENSION EXERCISES
        ═══════════════════════════════════════════════════════════════

        YOU MUST generate reading comprehension exercises as part of this test. This is NOT optional.

        READING EXERCISE MANDATORY RULES:
        - YOU MUST generate 1–2 reading exercises
        - Each reading exercise MUST contain: a coherent passage (500–700 words for B1-B2, 700+ for C1) PLUS 5–8 comprehension questions
        - Questions MUST be a mix of: main idea, detail, inference, and vocabulary-in-context
        - YOU ARE FORBIDDEN FROM generating grammar exercises in this section
        - Passage MUST be original, multi-paragraph text
        - Questions MUST use paraphrasing — no copying exact phrases from passage into answer options
        - YOU MUST create plausible but incorrect distractors for multiple choice questions

        READING DIFFICULTY:
        - A2: simple vocabulary, 300-400 words, direct comprehension
        - B1/B2: moderate vocabulary, 500-700 words, context-based with distractors
        - C1: advanced vocabulary, 700+ words, inference-heavy, nuanced

        READING RAG CONTEXT (inspiration only):
        {reading_data}
        """

        writing_block = ""
        if writing_enabled:
            writing_block = f"""
        ═══════════════════════════════════════════════════════════════
        SECTION C: WRITING EXERCISES
        ═══════════════════════════════════════════════════════════════

        YOU MUST generate writing exercises as part of this test. This is NOT optional.

        WRITING EXERCISE MANDATORY RULES:
        - YOU MUST generate 1 writing exercise
        - Types: email writing, letter writing, or essay
        - Must include: clear instructions, context (recipient + purpose), 3–4 bullet points, word count requirement
        - Word count by level: A1-A2: 50–80 words | B1: 100–120 words | B2: 300–350 words | C1: 400–600 words
        - Must clearly state formal or informal tone
        - Writing box must be rendered as a tall empty bordered box (min-height: 200px)

        CURRENT LEVEL FOR WRITING: {parsed_prompt.level}

        WRITING RAG CONTEXT (inspiration only):
        {writing_data}
        """

        combined_prompt = f"""YOU ARE AN EXPERT ENGLISH TEST DESIGNER AND WEB DESIGNER. GENERATE A COMPLETE, PRINT-READY HTML TEST FILE.

        ═══════════════════════════════════════════════════════════════
        ABSOLUTE RULES — VIOLATION = REJECTION
        ═══════════════════════════════════════════════════════════════
        1. Output ONLY raw HTML. No markdown. No code fences. No explanations. Start with <!DOCTYPE html>.
        2. CSS and HTML only — NO JavaScript whatsoever.
        3. Teacher input is supreme authority. RAG data is inspiration only.
        4. The file must be immediately convertible to PDF via WeasyPrint.

        ═══════════════════════════════════════════════════════════════
        WEASYPRINT CSS RULES — MANDATORY, NO EXCEPTIONS
        ═══════════════════════════════════════════════════════════════

        YOU MUST include this EXACT @page rule:
            @page {{
                size: A4;
                margin: 1.5cm 2cm;
            }}

        YOU MUST include this reset:
            * {{ box-sizing: border-box; }}
            body {{ margin: 0; padding: 0; background: #ffffff; }}
            .test-container {{ width: 100%; }}

        FORBIDDEN CSS (WeasyPrint will break):
            - display: flex  →  use display: table / table-cell instead
            - display: grid  →  use display: table / table-row / table-cell instead
            - vw, vh units   →  use %, cm, pt, px instead
            - max-width on .test-container  →  always use width: 100%
            - JavaScript-dependent CSS

        REQUIRED CSS PATTERNS:
            - Multi-column layouts (student info, answer key): display: table on parent, display: table-cell with explicit width on children
            - All widths of inner content elements: use % or explicit px, never vw

        PAGE BREAK RULES — CRITICAL, FOLLOW EXACTLY OR LAYOUT WILL BREAK:
            - ONLY the Answer Key gets: page-break-before: always
            - Every .exercise gets: page-break-inside: avoid — NOTHING ELSE
            - Every .section-divider gets BOTH:
                page-break-after: avoid      ← glues divider to the first exercise after it
                page-break-inside: avoid
                page-break-before: auto      ← NEVER use always on dividers
            - Every .exercise-title gets: page-break-after: avoid  ← title never orphaned from questions
            - NEVER use page-break-before: always on anything except .answer-key-section
            - NEVER use page-break-after: always anywhere
            - This ensures section dividers are NEVER alone on a page

        ═══════════════════════════════════════════════════════════════
        VISUAL DESIGN — MAKE IT LOOK LIKE A REAL PRINTED TEST
        ═══════════════════════════════════════════════════════════════

        The test must look like a professionally printed English exam from a school or language institute.
        Follow these design rules exactly:

        TYPOGRAPHY:
            - Primary font: Georgia, 'Times New Roman', serif  (body text, questions)
            - Accent font: 'Segoe UI', Tahoma, sans-serif  (headers, exercise titles, labels)
            - Body font-size: 11pt
            - Questions: 10.5pt, line-height: 1.7
            - Exercise titles: 12pt, bold, uppercase
            - h1 test title: 18pt, bold, uppercase, letter-spacing: 3px

        COLOR PALETTE — use EXACTLY these:
            - Primary dark: #1a2744  (header bg, answer key bg, borders)
            - Accent orange: #c0392b  (exercise number tags, section markers)
            - Light gray: #f5f5f5  (exercise background, reading passage bg)
            - White: #ffffff  (main page bg, writing box)
            - Muted text: #666666  (score tags, instructions, italic notes)

        HEADER (top of page):
            - Full-width dark bar (#1a2744) with white text
            - Test title centered, large, uppercase
            - Below: Level | Age Group | Total Score — separated by  |  characters
            - Thin bottom border: 4px solid #c0392b

        STUDENT INFO BAR:
            - 3 columns using display: table / table-cell
            - Each field: label + dotted underline (use border-bottom: 1.5px dotted #333)
            - Light gray background (#f5f5f5), padding 10px, margin-bottom 20px

        EXERCISE BLOCKS:
            - White background, border: 1.5px solid #ddd, padding: 16px
            - Margin-bottom: 20px
            - page-break-inside: avoid
            - Exercise number tag: small box, bg #c0392b, white text, font 9pt, float: right, padding: 3px 8px
            - Score tag: italic, small, gray, float: right — format: "( X pts )"
            - Exercise title: bold, uppercase, color #1a2744, border-left: 4px solid #c0392b, padding-left: 8px
            - Instructions: italic, color #666, font-size 10pt, margin-bottom 10px
            - Questions: numbered, 10.5pt, margin-bottom 8px
            - Answer lines: border-bottom: 1px solid #aaa, display: inline-block, min-width: 200px

        SECTION DIVIDERS (between Grammar / Reading / Writing):
            - Full-width bar: background #1a2744, color white, text-align center, padding 8px
            - Text: "SECTION A — GRAMMAR & VOCABULARY" etc., uppercase, letter-spacing 2px, font-size 10pt
            - MANDATORY page-break CSS on every .section-divider:
                page-break-before: auto;
                page-break-after: avoid;
                page-break-inside: avoid;

        MULTIPLE CHOICE options:
            - Display on same line or indented block, format: A) ... B) ... C) ...
            - Small circle before each: use a styled span with border-radius

        GAP FILL blanks:
            - Render as: _________________ (underscores, min-width 120px, border-bottom)

        READING PASSAGE:
            - Gray box (#f5f5f5), border-left: 4px solid #1a2744, padding 15px, font-style normal
            - Heading in bold above the passage

        WRITING BOX:
            - border: 1.5px solid #aaa, width: 100%, min-height: 200px, background: white
            - Lined paper effect: use repeating-linear-gradient for horizontal lines

        ANSWER KEY (last section):
            - page-break-before: always
            - Dark header bar (#1a2744), white text "ANSWER KEY — FOR TEACHER USE ONLY"
            - Red accent strip: 4px solid #c0392b above the section
            - Answers in 3-column table layout (display: table)
            - Each exercise answers in a box: border 1px solid #444, padding 10px, background #1e3055, color white
            - Exercise label bold, answers below in readable format

        FOOTER (bottom of each page using @page):
            @page {{
                @bottom-center {{
                    content: "— " counter(page) " —";
                    font-size: 9pt;
                    color: #999;
                }}
            }}

        ═══════════════════════════════════════════════════════════════
        CONTENT STRUCTURE — FOLLOW THIS ORDER EXACTLY
        ═══════════════════════════════════════════════════════════════

        1. HEADER BAR (title, level, age group, total score)
        2. STUDENT INFO BAR (Name / Date / Class)
        3. SECTION DIVIDER: "SECTION A — GRAMMAR & VOCABULARY"
        4. Grammar/vocabulary exercises (EXACTLY {grammar_vocab_amount} exercises)
        {f'5. SECTION DIVIDER: "SECTION B — READING COMPREHENSION"' if reading_enabled else ''}
        {f'6. Reading comprehension exercises' if reading_enabled else ''}
        {f'7. SECTION DIVIDER: "SECTION C — WRITING"' if writing_enabled else ''}
        {f'8. Writing exercise' if writing_enabled else ''}
        9. ANSWER KEY (always last, page-break-before: always)

        ═══════════════════════════════════════════════════════════════
        SCORING RULES
        ═══════════════════════════════════════════════════════════════

        - Every exercise MUST show its score: format "( X pts )" float right, before the title
        - The SUM of all exercise scores MUST equal the total score shown in the header
        - Grammar/vocab: 1 pt per question
        - Reading: 2 pts per question
        - Writing: assign 15 pts flat
        - Exercise numbering: sequential integers only — Ex. 1, 2, 3... NEVER skip or reset

        ═══════════════════════════════════════════════════════════════
        EXERCISE CONTENT RULES
        ═══════════════════════════════════════════════════════════════

        - Exactly {grammar_vocab_amount} grammar/vocabulary exercises
        - Each exercise: 6–10 questions, one grammar focus, unique sentences
        - Varied formats: multiple choice, gap fill, error correction, transformation, ordering, matching
        - No format repeated more than twice across the whole test
        - All contexts teen-relevant (school, travel, social media, sports, hobbies)
        - Difficulty strictly matching: {parsed_prompt.level}
        {reading_block}{writing_block}
        ═══════════════════════════════════════════════════════════════
        INPUT DATA
        ═══════════════════════════════════════════════════════════════

        Teacher input (PRIMARY SOURCE OF TRUTH): {parsed_prompt}
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
