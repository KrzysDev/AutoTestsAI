from backend.app.models.schemas import ParsedPrompt, PromptTestSection, Form, FormSection, CEFR_LEVEL_DESCRIPTIONS
from backend.app.config.language_configs import get_supported_languages, get_possible_language_codes
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
            * you can only generate {get_supported_languages()} exercises. If teacher demands something diffrent than english output general.

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
         - MUST FOLLOW: only possible language filed values are in this list: {get_possible_language_codes()}. YOU CAN NEVER PRINT IN THE 'language' FIELD ANYTHING ELSE. YOU HAVE TO CHOOSE ONE FROM THE LIST.
        
        #IMPORTANT INFORMATION
        1.Sections in provided format look like this:
            {json.dumps(PromptTestSection.model_json_schema(), indent=2)}

        2. They represent sections of a test. Possible values:
                task_type: Literal["vocabulary", "grammar", "reading", "writing"]
                description: string -> description of how exercise has to be created (implementation plan). Its either teachers idea or yours if teacher did not give enough information.
                subject: string (FREE TEXT) -> the grammar/vocabulary topic, e.g. "Present Simple", "Der Dativ", "Family vocabulary", "Fractions". NOT a fixed list — use whatever topic the teacher specifies or derive one from the request.
                retrival_subject: subject that will be searched in the database to retrive relevant data. Use ONLY grammar types. For example for english use only Present Simple For german only Perfekt, Prateritum. There must be only ONE retrival_subject per section. NEVER multiple like lists. ALWAYS one
                visuals: string -> description of how exercise has to look visually.
                amount : int
        
        #Teacher's request:
        {text}

        """

    def get_combined_html_generation_prompt(self, retrieval, reading_data, writing_data, parsed_prompt: Union[ParsedPrompt, Form], reading_enabled: bool, writing_enabled: bool):
        language = getattr(parsed_prompt, 'language', 'English')
        grammar_vocab_sections = [s for s in parsed_prompt.sections if s.task_type not in ("reading", "writing")]
        grammar_vocab_amount = sum(s.amount for s in grammar_vocab_sections)

        reading_block = ""
        if reading_enabled:
            rag_line = f"\nReading RAG context (inspiration only): {reading_data}" if reading_data else ""
            reading_block = f"""
## SECTION B: READING COMPREHENSION (mandatory)
- Generate 1–2 reading exercises
- Each: coherent original multi-paragraph passage + 5–8 comprehension questions
- Provide clear instructions (commands) for each exercise in the language the teacher used for their prompt.
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
- Include: clear instructions (commands) in the language the teacher used for their prompt, context (recipient+purpose), 3–4 bullet points, word count requirement
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

        combined_prompt = f"""You are an expert {language} test designer and web designer. Generate a complete, print-ready HTML test file. The content of the exercises (sentences, passages, options) must be in {language}.

# ABSOLUTE RULES (violation = rejection)
1. Output ONLY raw HTML starting with <!DOCTYPE html>. No markdown, no code fences, no explanations.
2. CSS+HTML only — zero JavaScript.
3. Teacher input overrides everything. RAG data is inspiration only.
4. Must be convertible to PDF via WeasyPrint.
5. Instructions and commands to exercises (e.g. "Fill in the blanks", "Choose the correct answer") MUST be in the language the teacher used to prompt you (see 'task' or 'additional_notes' in Teacher Input) unless the teacher explicitly requested otherwise.

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
- All answers in the solution key MUST strictly follow the transformation type requested in the task. Do not introduce alternative grammatical moods unless explicitly required.
- never use special sighns like '$\rightarrow$' or any other. Simple keyboard text and sighns.

# CONTENT STRUCTURE (follow this exact order)
{structure_block}

# SCORING
- Every exercise shows score: "( X pts )" float right
- Sum of scores = total score in header
- Grammar/vocab: 1pt/question | Reading: 2pts/question | Writing: 15pts flat
- Sequential numbering: Ex. 1, 2, 3… never skip or reset

# GRAMMAR & VOCABULARY EXERCISES (Section A)
- Exactly {grammar_vocab_amount} exercises, each 6–10 questions, one grammar focus, unique sentences
- Provide clear instructions (commands) for each exercise in the language the teacher used for their prompt.
- Formats: multiple choice, gap fill, error correction, transformation, ordering, matching — no format repeated 3+ times
- Contexts relevant to age group
- Difficulty: {parsed_prompt.level}
{reading_block}{writing_block}
# INPUT DATA
Teacher input (primary source of truth): {parsed_prompt}{rag_grammar_line}"""

        return combined_prompt

    def _get_cefr_block(self, level: str):
        desc = CEFR_LEVEL_DESCRIPTIONS.get(level, "No description available.")
        return f"""# CEFR PROFICIENCY LEVEL: {level}
{desc}
Use these criteria to ensure the complexity of the content (vocabulary, sentence structures, and cognitive load) matches the required level. DO NOT generate A1-level content for C1-level requests."""

    def _get_absolute_rules(self):
        return """# ABSOLUTE RULES (violation = rejection)
1. Output ONLY raw HTML starting with <!DOCTYPE html>. No markdown, no code fences, no explanations.
2. CSS+HTML only — zero JavaScript.
3. Teacher input overrides everything. RAG data is inspiration only.
4. Must be convertible to PDF via WeasyPrint."""

    def _get_weasyprint_css(self):
        return """# WEASYPRINT CSS
Required @page rule:
@page { size: A4; margin: 1.5cm 2cm; @bottom-center { content: "— " counter(page) " —"; font-size: 9pt; color: #999; } }

Required reset:
* { box-sizing: border-box; } body { margin:0; padding:0; background:#fff; } .test-container { width:100%; }

FORBIDDEN CSS (breaks WeasyPrint): display:flex, display:grid, vw/vh units, max-width on .test-container, JS-dependent CSS.
USE INSTEAD: display:table/table-cell for multi-column layouts. Use %, cm, pt, px for widths."""

    def _get_visual_design_rules(self, level: str):
        return f"""# VISUAL DESIGN
You have full creative freedom over colors, fonts, and aesthetic style. Design a professional, visually appealing exercise.
- Body font-size: 10–12pt, line-height ≥ 1.5
- Header: small bar with exercise title and level: {level}
- Student info: Name / Date / Class
- Exercise block: padding ≥ 12px, margin-bottom ≥ 15px. Must show score "( X pts )"
- Gap fill blanks: border-bottom underline, min-width ≥ 100px
- MCQ options: A) B) C) format"""

    def get_grammar_mcq_prompt(self, section: Union[PromptTestSection, FormSection], level: str, age_group: str, language: str = "English", retrieval: str = None):
        rag_line = f"\nGrammar RAG context (Tense definitions/Inspiration): {retrieval}" if retrieval else ""
        description = getattr(section, 'description', getattr(section, 'additional_comment', ''))
        return f"""You are an expert {language} test designer and web designer. Generate a complete, print-ready HTML file containing ONE Multiple Choice Grammar exercise. Generate all exercise content in {language}.

{self._get_cefr_block(level)}
{self._get_absolute_rules()}
{self._get_weasyprint_css()}
{self._get_visual_design_rules(level)}

# CONTENT: MULTIPLE CHOICE GRAMMAR
- Generate exactly ONE exercise with 10 questions.
- Format: 4 options (A, B, C, D) for each question.
- Subject: {section.subject}
- Level: {level}
- Age group: {age_group}
- Task description: {description}
- Every question is worth 1pt. Show total score.
- Sequential numbering: Ex. 1.

# INPUT DATA
Teacher requirements: {section}{rag_line}"""

    def get_grammar_gap_fill_prompt(self, section: Union[PromptTestSection, FormSection], level: str, age_group: str, language: str = "English", retrieval: str = None):
        rag_line = f"\nGrammar RAG context (Tense definitions/Inspiration): {retrieval}" if retrieval else ""
        description = getattr(section, 'description', getattr(section, 'additional_comment', ''))
        return f"""You are an expert {language} test designer and web designer. Generate a complete, print-ready HTML file containing ONE Gap Fill Grammar exercise. Generate all exercise content in {language}.

{self._get_cefr_block(level)}
{self._get_absolute_rules()}
{self._get_weasyprint_css()}
{self._get_visual_design_rules(level)}

# CONTENT: GAP FILL GRAMMAR
- Generate exactly ONE exercise with 10 sentences.
- Format: Open gap fill (no options) or with verbs in brackets to be conjugated.
- Subject: {section.subject}
- Level: {level}
- Age group: {age_group}
- Task description: {description}
- Every question is worth 1pt. Show total score.

# INPUT DATA
Teacher requirements: {section}{rag_line}"""

    def get_grammar_transformation_prompt(self, section: Union[PromptTestSection, FormSection], level: str, age_group: str, language: str = "English", retrieval: str = None):
        rag_line = f"\nGrammar RAG context (Tense definitions/Inspiration): {retrieval}" if retrieval else ""
        description = getattr(section, 'description', getattr(section, 'additional_comment', ''))
        return f"""You are an expert {language} test designer and web designer. Generate a complete, print-ready HTML file containing ONE Key Word Transformation exercise. Generate all exercise content in {language}.

{self._get_cefr_block(level)}
{self._get_absolute_rules()}
{self._get_weasyprint_css()}
{self._get_visual_design_rules(level)}

# CONTENT: KEY WORD TRANSFORMATION
- Generate exactly ONE exercise with 6–8 questions.
- Format: A sentence followed by a key word and a second sentence with a gap. The second sentence must have the same meaning as the first.
- Subject: {section.subject}
- Level: {level}
- Age group: {age_group}
- Task description: {description}
- Every question is worth 2pts. Show total score.

# INPUT DATA
Teacher requirements: {section}{rag_line}"""

    def get_vocabulary_matching_prompt(self, section: Union[PromptTestSection, FormSection], level: str, age_group: str, language: str = "English", retrieval: str = None):
        rag_line = f"\nVocabulary RAG context (Inspiration): {retrieval}" if retrieval else ""
        description = getattr(section, 'description', getattr(section, 'additional_comment', ''))
        return f"""You are an expert {language} test designer and web designer. Generate a complete, print-ready HTML file containing ONE Vocabulary Matching exercise. Generate all exercise content in {language}.

{self._get_cefr_block(level)}
{self._get_absolute_rules()}
{self._get_weasyprint_css()}
{self._get_visual_design_rules(level)}

# CONTENT: VOCABULARY MATCHING
- Generate exactly ONE exercise with 10–12 items.
- Format: Match words to definitions, synonyms, or pictures (descriptions). Use display:table for a clear two-column layout.
- Subject: {section.subject}
- Level: {level}
- Age group: {age_group}
- Task description: {description}
- Every item is worth 1pt.

# INPUT DATA
Teacher requirements: {section}{rag_line}"""

    def get_reading_mcq_prompt(self, section: Union[PromptTestSection, FormSection], level: str, age_group: str, language: str = "English", retrieval: str = None):
        rag_line = f"\nReading RAG context (Inspiration): {retrieval}" if retrieval else ""
        description = getattr(section, 'description', getattr(section, 'additional_comment', ''))
        return f"""You are an expert {language} test designer and web designer. Generate a complete, print-ready HTML file containing ONE Reading Comprehension (Multiple Choice) exercise. Generate all exercise content in {language}.

{self._get_cefr_block(level)}
{self._get_absolute_rules()}
{self._get_weasyprint_css()}

# VISUAL DESIGN
- Reading passage: visually distinct container, padding ≥ 12px
- MCQ options: A) B) C) D) format

# CONTENT: READING MCQ
- Generate 1 original multi-paragraph passage + 5–8 Multiple Choice questions.
- Subject/Topic: {section.subject}
- Level: {level}
- Age group: {age_group}
- Task description: {description}
- Question types: main idea, detail, inference, vocabulary-in-context.
- Passage length: A2: 300w | B1/B2: 500w | C1: 700w

# INPUT DATA
Teacher requirements: {section}{rag_line}"""

    def get_reading_true_false_prompt(self, section: Union[PromptTestSection, FormSection], level: str, age_group: str, language: str = "English", retrieval: str = None):
        rag_line = f"\nReading RAG context (Inspiration): {retrieval}" if retrieval else ""
        description = getattr(section, 'description', getattr(section, 'additional_comment', ''))
        return f"""You are an expert {language} test designer and web designer. Generate a complete, print-ready HTML file containing ONE Reading Comprehension (True/False) exercise. Generate all exercise content in {language}.

{self._get_cefr_block(level)}
{self._get_absolute_rules()}
{self._get_weasyprint_css()}

# CONTENT: READING TRUE/FALSE
- Generate 1 original multi-paragraph passage + 8–10 True/False/Not Given questions.
- Subject/Topic: {section.subject}
- Level: {level}
- Age group: {age_group}
- Task description: {description}

# INPUT DATA
Teacher requirements: {section}{rag_line}"""

    def get_writing_email_prompt(self, section: Union[PromptTestSection, FormSection], level: str, age_group: str, language: str = "English", retrieval: str = None):
        rag_line = f"\nWriting RAG context (Inspiration): {retrieval}" if retrieval else ""
        description = getattr(section, 'description', getattr(section, 'additional_comment', ''))
        return f"""You are an expert {language} test designer and web designer. Generate a complete, print-ready HTML file containing ONE Informal Email/Letter Writing task. Generate all exercise content in {language}.

{self._get_cefr_block(level)}
{self._get_absolute_rules()}
{self._get_weasyprint_css()}

# VISUAL DESIGN
- Writing box: bordered, width:100%, min-height:250px

# CONTENT: INFORMAL WRITING
- Generate 1 informal email/letter task.
- Include: Clear context, 3 bullet points to cover.
- Subject/Topic: {section.subject}
- Level: {level}
- Age group: {age_group}
- Word count: {level} level appropriate (A2: 80, B1: 120, B2: 180).

# INPUT DATA
Teacher requirements: {section}{rag_line}"""

    def get_writing_essay_prompt(self, section: Union[PromptTestSection, FormSection], level: str, age_group: str, language: str = "English", retrieval: str = None):
        rag_line = f"\nWriting RAG context (Inspiration): {retrieval}" if retrieval else ""
        description = getattr(section, 'description', getattr(section, 'additional_comment', ''))
        return f"""You are an expert {language} test designer and web designer. Generate a complete, print-ready HTML file containing ONE Formal Essay Writing task. Generate all exercise content in {language}.

{self._get_cefr_block(level)}
{self._get_absolute_rules()}
{self._get_weasyprint_css()}

# VISUAL DESIGN
- Writing box: bordered, width:100%, min-height:400px

# CONTENT: FORMAL ESSAY
- Generate 1 formal essay task (opinion or for/against).
- Include: Essay prompt, 2 given points + 1 own idea requirement.
- Subject/Topic: {section.subject}
- Level: {level}
- Age group: {age_group}
- Word count: B2: 140-190, C1: 220-260.

# INPUT DATA
Teacher requirements: {section}{rag_line}"""

    def get_json_exercise_prompt(self, section: Union[PromptTestSection, FormSection], level: str, age_group: str, language: str = "English", retrieval: str = None):
        rag_line = f"\nRAG context (Inspiration): {retrieval}" if retrieval else ""
        description = getattr(section, 'description', getattr(section, 'additional_comment', ''))
        cefr_desc = CEFR_LEVEL_DESCRIPTIONS.get(level, "")
        
        return f"""You are an expert {language} test designer. Generate ONE exercise in a STRICT JSON format.

# CEFR LEVEL: {level}
{cefr_desc}

# EXERCISE REQUIREMENTS
- Type: {section.task_type}
- Subject: {section.subject}
- Level: {level}
- Age group: {age_group}
- Task description: {description}
- Generate at least 5-10 items/questions.
- Language: {language}

# OUTPUT FORMAT (JSON ONLY)
{{
  "id": "{section.subject.lower().replace(' ', '-')}_{section.task_type}",
  "language": "{language}",
  "metadata": {{
    "subject": "{section.subject}",
    "cefr": "{level}",
    "topic": "{section.subject}",
    "difficulty": "medium"
  }},
  "content": {{
    "type": "{section.task_type}",
    "instruction": "<student-facing instruction in {language}>",
    "body": "<full exercise content: sentences, gaps, options, etc.>",
    "answer_key": "<correct answers keyed to items in body>"
  }}
}}

RULES:
1. Return ONLY the JSON object. No markdown fences like ```json or ```, no extra text.
2. Ensure the JSON is valid and escaped correctly.
3. Content must strictly follow the CEFR level difficulty rules.

{rag_line}"""


    def get_exercise_parsing_prompt(self, raw_content: str, subject: str, level: str, task_type: str, language: str = "English"):
        return f"""You are a data extractor. Convert the following raw exercise content (HTML/Text) into a structured JSON format.

# RAW CONTENT
{raw_content}

# TARGET JSON SCHEMA
{{
  "id": "{subject.lower().replace(' ', '-')}_{task_type}",
  "language": "{language}",
  "metadata": {{
    "subject": "{subject}",
    "cefr": "{level}",
    "topic": "{subject}",
    "difficulty": "medium"
  }},
  "content": {{
    "type": "{task_type}",
    "instruction": "<extract student-facing instruction>",
    "body": "<extract full exercise content: sentences, gaps, options, etc.>",
    "answer_key": "<extract correct answers keyed to items in body>"
  }}
}}

RULES:
1. Return ONLY the JSON object. No markdown fences.
2. Ensure the content is extracted exactly as it appears in the raw text.
3. If answer key is missing, try to solve the exercise yourself and provide it."""



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
