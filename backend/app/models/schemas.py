from pydantic import BaseModel, field_validator, Field, ConfigDict

from typing import Literal, Union, Optional


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
