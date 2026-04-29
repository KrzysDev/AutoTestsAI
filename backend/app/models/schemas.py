from pydantic import BaseModel, field_validator, Field, ConfigDict

from typing import Literal, Union, Optional

CEFR_LEVEL_DESCRIPTIONS = {
    "A1": "Beginner: Can understand and use familiar everyday expressions and very basic phrases aimed at the satisfaction of needs of a concrete type. Can introduce themselves and others and ask/answer questions about personal details. Interaction is simple, provided the other person talks slowly and clearly.",
    "A2": "Elementary: Can understand sentences and frequently used expressions related to areas of most immediate relevance (e.g. personal info, shopping, local geography, employment). Can communicate in simple and routine tasks requiring a simple and direct exchange of information. Can describe in simple terms aspects of their background and immediate environment.",
    "B1": "Intermediate: Can understand the main points of clear standard input on familiar matters regularly encountered in work, school, leisure, etc. Can deal with most situations likely to arise while travelling. Can produce simple connected text on topics which are familiar or of personal interest. Can describe experiences, events, dreams, and ambitions, and briefly give reasons for opinions.",
    "B2": "Upper Intermediate: Can understand the main ideas of complex text on both concrete and abstract topics, including technical discussions in their field of specialization. Can interact with a degree of fluency and spontaneity that makes regular interaction with native speakers possible without strain. Can produce clear, detailed text on a wide range of subjects and explain a viewpoint on topical issues.",
    "C1": "Advanced: Can understand a wide range of demanding, longer texts and recognize implicit meaning. Can express themselves fluently and spontaneously without much obvious searching for expressions. Can use language flexibly and effectively for social, academic, and professional purposes. Can produce clear, well-structured, detailed text on complex subjects.",
    "C2": "Proficiency: Can understand with ease virtually everything heard or read. Can summarize information from different spoken and written sources, reconstructing arguments and accounts in a coherent presentation. Can express themselves spontaneously, very fluently and precisely, differentiating finer shades of meaning even in the most complex situations."
}


class PromptRequest(BaseModel):
    prompt: str


class HtmlRequest(BaseModel):
    html: str


class PromptTestSection(BaseModel):
    task_type: Literal["vocabulary", "grammar", "reading", "writing"]
    description: str
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
    visuals: str
    amount: int

class ParsedPrompt(BaseModel):
    task : str
    level : Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    age_group : Literal["kids", "teens", "adults"]
    sections : list[PromptTestSection]
    total_amount : int = 20


class RetrivalQueries(BaseModel):
    queries : list[Literal["vocabulary", "grammar", "reading", "writing"]]




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
    task_type: Literal["vocabulary", "grammar", "reading", "writing", "other"]
    subject: str
    amount: int
    additional_comment: Optional[str] = None


class Form(BaseModel):
    level: Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    age_group: Literal["kids", "teens", "adults"]
    sections: list[FormSection]
    total_amount: Optional[int] = None
    additional_notes: Optional[str] = None


class TestSurveyRequest(BaseModel):
    form: Form
