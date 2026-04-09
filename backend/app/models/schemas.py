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


#section in transformed prompt. Section explained to AI model
class PromptTestSection(BaseModel):
    section_type: str
    subject : str
    amount : int

class FirstLayerRules(BaseModel):
    task_info: str
    level_info: str
    target_age_info: str
    sections_info: str
    total_tasks_info: str
    output_rule_info: str

class TransformedPrompt(BaseModel):
    task: str 
    level : Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    target_age: str
    sections: list[PromptTestSection]
    total_tasks: int

class RetrievalInstructions(BaseModel):
    grammar_instructions: list[RetrivedChunk] = Field(alias="Grammar_Instructions")
    exercise_instructions: list[RetrivedChunk] = Field(alias="Exercise_Instructions")
    
    model_config = ConfigDict(populate_by_name=True)  

class RetrievalData(BaseModel):
    instructions: RetrievalInstructions = Field(alias="Instructions")
    
    model_config = ConfigDict(populate_by_name=True)  

class GenerationPrompt(BaseModel):
    twoja_rola: str = Field(
        default="Jesteś ekspertem w tworzeniu materiałów dydaktycznych do nauki języków obcych. Twoim zadaniem jest stworzenie jednego zadania na podstawie dostarczonych danych z retrivalu.",
        alias="twoja rola"
    )
    zasady: str = Field(
        default="W polu 'dane z retrival' podane są przykładowe zadania na których MUSISZ się wzorować tworząc nowe podobnego rodzaju. Skup sie na poziomie jaki reprezentuja i jak są skoonstruowane. Poniżej znajdziesz też instrukcje w jaki sposób krok po kroku stworzyć tego typu zadanie. Musisz zwrócić wyłącznie JSON w wymaganym formacie. Nic więcej poza nim. Nie dodawaj nic przed ani po jsonie w tym znaków markdown takich jak ```json lub ```",
        alias="zasady"
    )
    szczegóły_pól: str = Field(
        default="level - poziom językowy CEFR (A1, A2, B1...C2), age_group - docelowa grupa wiekowa (kids, teens, adults), task_type - typ zadania (np. vocabulary, grammar, reading etc. musisz wybrac jeden), topic - temat zadania (np. present simple, present contionous, reading etc. musisz wybrac jeden), amount - ilość wystąpień / ile zadan musisz w tej liscie tego typu stworzyć (wybierz dowolnie, chyba że została podana przez nauczyciela)",
        alias="szczegóły_pół"
    )
    prosba_nauczyciela: str = Field(alias="prosba_nauczyciela")
    dane_z_retrieval: RetrievalData = Field(alias="dane z retrival")
    wymagany_format_json: dict = Field(
        default={
            "Question": {
                "content": {
                    "instruction": "",
                    "body": ""
                }
            }
        },
        alias="wymagany format json"
    )

    model_config = ConfigDict(populate_by_name=True)
    



