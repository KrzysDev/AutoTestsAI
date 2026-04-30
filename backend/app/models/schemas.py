from pydantic import BaseModel, field_validator, Field, ConfigDict

from typing import Literal, Union, Optional

# Shared type alias for exercise task types — used in PromptTestSection, FormSection, RetrivalQueries.
# To add a new task type, change it here only.
TASK_TYPES = Literal["vocabulary", "grammar", "reading", "writing"]

CEFR_LEVEL_DESCRIPTIONS = {
    "A1": (
        "Description: Beginner level. Can understand and use familiar everyday expressions and very basic phrases. "
        "Vocabulary Focus: Basic everyday objects, colors, numbers, family members, common verbs, simple greetings. "
        "Task Difficulty: Very Low. Tasks should be extremely simple: identification, direct matching, single-word answers. "
        "Cognitive Load: Minimal. Very short sentences, the most common words only. No complex grammar structures."
    ),
    "A2": (
        "Description: Elementary level. Can understand frequently used expressions in areas of immediate relevance. Can communicate in simple, routine tasks. "
        "Vocabulary Focus: Daily routines, shopping, basic hobbies, simple travel, basic emotions. "
        "Task Difficulty: Low. Tasks involve basic context understanding, simple MCQ, or short gap-fills in isolated sentences. "
        "Cognitive Load: Low. Simple sentence structures, common vocabulary, no ambiguity."
    ),
    "B1": (
        "Description: Intermediate level. Can understand the main points of clear standard input on familiar matters. Can produce simple connected text. "
        "Vocabulary Focus: Work, education, leisure, travel, personal opinions. "
        "Task Difficulty: Moderate. Tasks require connecting ideas, understanding short paragraphs, and using common grammatical structures in context. "
        "Cognitive Load: Medium. Multi-clause sentences, moderate vocabulary range, some implicit meaning."
    ),
    "B2": (
        "Description: Upper Intermediate level. Can understand main ideas of complex text on concrete and abstract topics. Can interact with fluency and spontaneity. "
        "Vocabulary Focus: Abstract concepts, technical vocabulary, advantages/disadvantages, social issues. "
        "Task Difficulty: High. Tasks involve identifying tone, paraphrasing complex ideas, advanced vocabulary, word formation and sentence transformations. "
        "Cognitive Load: High. Complex sentence structures, sophisticated vocabulary, inference required."
    ),
    "C1": (
        "Description: Advanced level. Can understand a wide range of demanding texts and recognise implicit meaning. Can use language flexibly for academic and professional purposes. "
        "Vocabulary Focus: Idiomatic expressions, nuanced vocabulary, academic jargon, implicit meaning, irony. "
        "Task Difficulty: Very High. Tasks require detecting subtle nuances, understanding complex arguments, rare or highly specific vocabulary and structures. "
        "Cognitive Load: Very High. Long, multi-layered texts, inference from context, high precision required."
    ),
    "C2": (
        "Description: Proficiency level. Can understand with ease virtually everything heard or read. Can express spontaneously, very fluently and precisely. "
        "Vocabulary Focus: Complete mastery of sophisticated vocabulary, subtle nuances, synthesis of complex information from multiple sources. "
        "Task Difficulty: Professional/Native. Tasks involve synthesizing diverse information, extremely complex sentence structures, absolute precision in meaning. "
        "Cognitive Load: Maximum. Near-native complexity, idiomatic subtlety, discourse-level coherence expected."
    )
}


class PromptRequest(BaseModel):
    prompt: str


class HtmlRequest(BaseModel):
    html: str


class PromptTestSection(BaseModel):
    task_type: TASK_TYPES
    description: str
    subject: str  # Free-text topic — e.g. "Present Simple", "Der Dativ", "Fractions"
    visuals: str
    amount: int

class ParsedPrompt(BaseModel):
    task : str
    language : str = "English"  # Language of the test, e.g. "English", "German", "French"
    level : Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    age_group : Literal["kids", "teens", "adults"]
    sections : list[PromptTestSection]
    total_amount : int = 20


class RetrivalQueries(BaseModel):
    queries : list[TASK_TYPES]




class TestGeneratorResponseMetadataRetrival(BaseModel):
    regular: str
    writing: str
    reading: str


class TestGeneratorResponseMetadata(BaseModel):
    prompt: str
    parsed_prompt: str
    tokens: int
    time: float
    average_time: float
    retrival: TestGeneratorResponseMetadataRetrival



class TestGeneratorHTMLResponse(BaseModel):
    response: str
    metadata: TestGeneratorResponseMetadata


class FormSection(BaseModel):
    task_type: TASK_TYPES
    subject: str
    amount: int
    additional_comment: Optional[str] = None


class Form(BaseModel):
    language: str = "English"  # Language of the test, e.g. "English", "German", "French"
    level: Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    age_group: Literal["kids", "teens", "adults"]
    sections: list[FormSection]
    total_amount: Optional[int] = None
    additional_notes: Optional[str] = None


class TestSurveyRequest(BaseModel):
    form: Form
