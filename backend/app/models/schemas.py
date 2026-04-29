from pydantic import BaseModel, field_validator, Field, ConfigDict

from typing import Literal, Union, Optional

CEFR_LEVEL_DESCRIPTIONS = {
    "A1": (
        "Description: Beginner level. Can understand and use familiar everyday expressions and very basic phrases aimed at the satisfaction of needs of a concrete type. Can introduce him/herself and others and can ask and answer questions about personal details such as where he/she lives, people he/she knows and things he/she has. Can interact in a simple way provided the other person talks slowly and clearly and is prepared to help. "
        "Vocabulary Focus: Colors, numbers, family members, basic household objects, common verbs (to be, to have, to go), basic greetings, and personal pronouns. "
        "Sentence Examples: 'Hello, my name is John.', 'I have a big red car.', 'Where is the library?', 'Nice to meet you.'"
    ),
    "A2": (
        "Description: Elementary level. Can understand sentences and frequently used expressions related to areas of most immediate relevance (e.g. very basic personal and family information, shopping, local geography, employment). Can communicate in simple and routine tasks requiring a simple and direct exchange of information on familiar and routine matters. Can describe in simple terms aspects of his/her background, immediate environment and matters in areas of immediate need. "
        "Vocabulary Focus: Daily routines, shopping terms, basic hobbies and leisure activities, simple travel and transport, basic emotions and physical descriptions. "
        "Sentence Examples: 'I went to the park yesterday.', 'She is much taller than her brother.', 'Can you tell me the way to the station?', 'I like cooking in my free time.'"
    ),
    "B1": (
        "Description: Intermediate level. Can understand the main points of clear standard input on familiar matters regularly encountered in work, school, leisure, etc. Can deal with most situations likely to arise whilst travelling in an area where the language is spoken. Can produce simple connected text on topics which are familiar or of personal interest. Can describe experiences and events, dreams, hopes & ambitions and briefly give reasons and explanations for opinions and plans. "
        "Vocabulary Focus: Work and employment, education and school life, leisure and travel experiences, expressing personal opinions, talking about plans, dreams, and ambitions. "
        "Sentence Examples: 'I have lived in this city for over five years.', 'If it rains tomorrow, we will stay at home.', 'I believe that this book is worth reading because...', 'I am planning to study abroad next year.'"
    ),
    "B2": (
        "Description: Upper Intermediate level. Can understand the main ideas of complex text on both concrete and abstract topics, including technical discussions in his/her field of specialisation. Can interact with a degree of fluency and spontaneity that makes regular interaction with native speakers quite possible without strain for either party. Can produce clear, detailed text on a wide range of subjects and explain a viewpoint on a topical issue giving the advantages and disadvantages of various options. "
        "Vocabulary Focus: Concrete and abstract concepts, technical and professional terminology, expressing advantages and disadvantages, complex social issues, and detailed descriptions of experiences. "
        "Sentence Examples: 'If I had more free time, I would certainly take up a new hobby.', 'The problem currently being discussed is far more complex than it appears.', 'Despite the challenging circumstances, they managed to succeed.', 'It is generally argued that technology has changed our lives.'"
    ),
    "C1": (
        "Description: Advanced level. Can understand a wide range of demanding, longer texts, and recognise implicit meaning. Can express him/herself fluently and spontaneously without much obvious searching for expressions. Can use language flexibly and effectively for social, academic and professional purposes. Can produce clear, well-structured, detailed text on complex subjects, showing controlled use of organisational patterns, connectors and cohesive devices. "
        "Vocabulary Focus: Idiomatic expressions, nuanced and sophisticated vocabulary, academic and professional jargon, understanding implicit meaning and subtle irony. "
        "Sentence Examples: 'Hardly had the meeting started when the fire alarm rang.', 'Had it not been for your invaluable assistance, we would never have finished.', 'It is absolutely essential that everyone be aware of the new regulations.', 'The implications of this decision are far-reaching and multifaceted.'"
    ),
    "C2": (
        "Description: Proficiency level. Can understand with ease virtually everything heard or read. Can summarise information from different spoken and written sources, reconstructing arguments and accounts in a coherent presentation. Can express him/herself spontaneously, very fluently and precisely, differentiating finer shades of meaning even in more complex situations. "
        "Vocabulary Focus: Complete mastery of sophisticated vocabulary, subtle nuances of meaning, ability to summarise and synthesize information from diverse and complex sources. "
        "Sentence Examples: 'The sheer magnitude of the discovery was, to put it mildly, quite staggering.', 'Lest the message be misunderstood, it was repeated with even greater emphasis.', 'So subtle were the changes in the atmosphere that they almost went completely unnoticed.', 'The complexity of the situation defies any simple explanation.'"
    )
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
