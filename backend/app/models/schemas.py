from pydantic import BaseModel, field_validator, Field, ConfigDict

from typing import Literal, Union, Optional

class PromptTestSection(BaseModel):
    task_type: Literal["vocabulary", "grammar", "reading", "writing"]
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

class PDFExercise(BaseModel):
    instruction: str
    body : str
    formatting_type: Literal["Listening-Multiple-Choice", "Listeninig-Match-Inf", "Listening-Insert", "Reading-Multiple-Choice", "Reading-Match-Headings", "True-False"]

class PDFTest(BaseModel):
    exercises: list[PDFExercise]
