from pydantic import BaseModel, field_validator, Field, ConfigDict
from typing import Literal, Union, Optional


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
    score: Optional[float] = None

class Question(BaseModel):
    instruction : str
    body : str


class Group(BaseModel):
    questions: list[Question]
    answers: list[str]


class Test(BaseModel):
    groups: list[Group]


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


#section format in test. Used to print it on pdf and as model output
class GeneratedTestSection(BaseModel):
    instruction: str
    body: str

