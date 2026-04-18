from pydantic import BaseModel, field_validator, Field, ConfigDict

from typing import Literal, Union, Optional


class PromptRequest(BaseModel):
    prompt: str


class HtmlRequest(BaseModel):
    html: str



#data types needed to generate test as a raw text

class PromptTestSection(BaseModel):
    task_type: Literal["vocabulary", "grammar", "reading", "writing"]
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
    amount : int

class Exercise(BaseModel):
    instruction: str
    body: str

class GeneratedTest(BaseModel):
    exercises: list[Exercise]

class ParsedPrompt(BaseModel):
    task : str
    level : Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    age_group : Literal["kids", "teens", "adults"]
    sections : list[PromptTestSection]
    total_amount : int = 20


class RetrivalQueries(BaseModel):
    queries : list[Literal["vocabulary", "grammar", "reading", "writing"]]

class TestGeneratorRequest(BaseModel):
    prompt: str
    level: Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    age_group: Literal["kids", "teens", "adults"]
    total_amount: int = 20

class TestFixRequest(BaseModel):
    generated_test: GeneratedTest
    teacher_prompt: str

# Data types to make generated test pretty

class MultipleChoiceQuestion(BaseModel):
    question: str
    options: list[str]
    answer: Optional[str] = None

class MultipleChoiceExercise(BaseModel):
    task_type: Literal["multiple_choice"] = "multiple_choice"
    instruction: str
    questions: list[MultipleChoiceQuestion]

class MatchingExercise(BaseModel):
    task_type: Literal["matching"] = "matching"
    instruction: str
    left_column: list[str]
    right_column: list[str]
    answers: Optional[dict[str, str]] = None

class TrueFalseExercise(BaseModel):
    task_type: Literal["true_false"] = "true_false"
    instruction: str
    statements: list[str]
    answers: Optional[list[bool]] = None

class WordFormationItem(BaseModel):
    sentence_with_gap: str
    root_word: str

class WordFormationExercise(BaseModel):
    task_type: Literal["word_formation"] = "word_formation"
    instruction: str
    items: list[WordFormationItem]

class GapFillExercise(BaseModel):
    task_type: Literal["gap_fill"] = "gap_fill"
    instruction: str
    passage: str
    choices: list[str]

class TransformationItem(BaseModel):
    original_sentence: str
    key_word: str
    sentence_with_gap: str

class TransformationExercise(BaseModel):
    task_type: Literal["transformation"] = "transformation"
    instruction: str
    items: list[TransformationItem]

class WritingExercise(BaseModel):
    task_type: Literal["writing"] = "writing"
    instruction: str
    prompt: str
    word_count_range: Optional[str] = None

class ClozeOption(BaseModel):
    gap_number: int
    options: list[str]

class ClozeExercise(BaseModel):
    task_type: Literal["cloze"] = "cloze"
    instruction: str
    passage: str
    options_per_gap: list[ClozeOption]

class SimpleTextExercise(BaseModel):
    task_type: Literal["simple_text"] = "simple_text"
    instruction: str
    body: str

# Use a type alias for easy reference
PDFExercise = Union[
    MultipleChoiceExercise,
    MatchingExercise,
    TrueFalseExercise,
    WordFormationExercise,
    GapFillExercise,
    TransformationExercise,
    WritingExercise,
    ClozeExercise,
    SimpleTextExercise
]

class PDFTest(BaseModel):
    exercises: list[PDFExercise]


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

class TestGeneratorResponse(BaseModel):
    response: GeneratedTest
    metadata: TestGeneratorResponseMetadata

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
