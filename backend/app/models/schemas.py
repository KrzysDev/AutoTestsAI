from pydantic import BaseModel, field_validator

from typing import Literal
from typing import Union

class ChunkMetadata(BaseModel):

    subject: str
    content: Union[str, dict]

class Chunk(BaseModel):
    id: str

    section: Literal["vocabulary", "grammar", "listening", "reading"]

    language: Literal["en", "de", "eng", "ger"]

    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]

    metadata: ChunkMetadata

    @field_validator("level")
    @classmethod
    def no_combined_levels(cls, v: str) -> str:
        if "/" in v or "-" in v:
            raise ValueError(f"Level must be a single value, received: '{v}'")
        return v

class RetrivedChunk(BaseModel):
    payload: Chunk
    score: float

class Question(BaseModel):
    content : {
        "instruction" : str,
        "body" : str
    }

class Group(BaseModel):
    questions : list[Question]
    answers : list[str]

class Test(BaseModel):
    groups : list[Group]


class TeacherRequestClassification(BaseModel):
    text: str
    classification: str

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, v: str) -> str:
        if v.lower() not in ["general", "test", "general\n", "test\n, \ngeneral", "\ntest"]:
            if v.startswith("general"):
                return "general"
            elif v.startswith("test"):
                return "test"
            else:
                raise ValueError(f"Classification must be either 'general' or 'test', received: '{v}'")
        return v.lower()


class TestGeneratorRequest(BaseModel):
    language: Literal["en", "de", "eng", "ger"]
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    topic: str
    group_count: int = 2

class Exercise(BaseModel):
    type : str
    subject : str
    amount : int


class AgenticPromptFirstLayer(BaseModel):
    twoja_rola : str
    zasady : {
        "task info" : str,
        "level info" : str,
        "target age info" : str,
        "sections info" : str,
        "total tasks info" : str,
        "output rule info" : str
    }
    dane_z_retrival : dict[str, Union[str, list[Exercise]]]
    Instructions : list[str]
    wymagany_format_json : Question

class AgenticPromptSecondLayer(BaseModel):
    twoja_rola : str
    zasady : str
    dane_z_retrival : dict[str, Union[str, list[Exercise]]]
    Instructions : list[str]
    wymagany_format_json : Question

    