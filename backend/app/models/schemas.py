from pydantic import BaseModel, field_validator, Field, ConfigDict

from typing import Literal, Union, Optional

CEFR_LEVEL_DESCRIPTIONS = {
    "A1": (
        "Description: Beginner level. Can understand and use familiar everyday expressions and very basic phrases aimed at the satisfaction of needs of a concrete type. Can introduce him/herself and others and can ask and answer questions about personal details. Can interact in a simple way. "
        "Vocabulary Focus: Colors, numbers, family members, basic household objects, common verbs, basic greetings. "
        "Sentence Examples: 'Hello, my name is John.', 'I have a big red car.', 'Where is the library?' "
        "Task Difficulty: Very Low. Tasks should be extremely simple, focusing on identification and direct matching. "
        "Example Task (Matching): Match the following words with their Polish translations: 1. Apple, 2. Book, 3. Chair, 4. Dog, 5. Elephant, 6. Father, 7. Girl, 8. House."
    ),
    "A2": (
        "Description: Elementary level. Can understand sentences and frequently used expressions related to areas of most immediate relevance. Can communicate in simple and routine tasks requiring a simple and direct exchange of information. "
        "Vocabulary Focus: Daily routines, shopping terms, basic hobbies, simple travel, basic emotions. "
        "Sentence Examples: 'I went to the park yesterday.', 'She is much taller than her brother.', 'I like cooking.' "
        "Task Difficulty: Low. Tasks involve basic context understanding, simple multiple-choice questions, or short gap-fills in isolated sentences. "
        "Example Task (MCQ): Choose the correct answer: 1. I (go/goes/going) to school. 2. She (is/are/am) happy. 3. They (have/has) a dog. 4. We (was/were) at home. 5. He (do/does) his homework. 6. Look! It (rains/is raining)."
    ),
    "B1": (
        "Description: Intermediate level. Can understand the main points of clear standard input on familiar matters. Can deal with most situations while travelling. Can produce simple connected text on topics which are familiar or of personal interest. "
        "Vocabulary Focus: Work and employment, education, leisure and travel experiences, expressing personal opinions. "
        "Sentence Examples: 'I have lived in this city for over five years.', 'If it rains tomorrow, we will stay at home.' "
        "Task Difficulty: Moderate. Tasks require connecting ideas, understanding simple paragraphs, and using common grammatical structures in context. "
        "Example Task (Gap Fill): Fill in the gaps with ONE word: 1. I have ___ waiting for you. 2. If I ___ you, I would go. 3. The book ___ written by him. 4. She is interested ___ music. 5. He is the man ___ lives next door. 6. They ___ not seen the movie yet."
    ),
    "B2": (
        "Description: Upper Intermediate level. Can understand the main ideas of complex text on both concrete and abstract topics. Can interact with a degree of fluency and spontaneity. Can produce clear, detailed text. "
        "Vocabulary Focus: Abstract concepts, technical terminology, expressing advantages/disadvantages, social issues. "
        "Sentence Examples: 'If I had more free time, I would certainly take up a new hobby.', 'Despite the circumstances, they succeeded.' "
        "Task Difficulty: High. Tasks involve identifying tone, paraphrasing complex ideas, and using advanced vocabulary. Word formation and sentence transformations are common. "
        "Example Task (Transformations): Rewrite the sentence using the word given: 1. I'm sure he is tired. (MUST) -> He... 2. It was a mistake to buy this. (SHOULDN'T) -> I... 3. They are building a new road. (BEING) -> A new road... 4. 'I am sorry,' he said. (APOLOGIZED) -> He... 5. Although it was cold, we went out. (DESPITE) -> ... 6. He started here in 2010. (WORKING) -> He has..."
    ),
    "C1": (
        "Description: Advanced level. Can understand a wide range of demanding, longer texts, and recognise implicit meaning. Can express him/herself fluently and spontaneously. Can use language flexibly and effectively for social, academic and professional purposes. "
        "Vocabulary Focus: Idiomatic expressions, nuanced vocabulary, academic jargon, implicit meaning, irony. "
        "Sentence Examples: 'Hardly had the meeting started when the fire alarm rang.', 'Had it not been for your help, we would have failed.' "
        "Task Difficulty: Very High. Tasks require detecting subtle nuances, understanding complex arguments, and using rare or highly specific vocabulary and structures. "
        "Example Task (Vocabulary Nuances): Choose the best word to fit the gap: 1. The manager ___ the importance of safety. (stressed/highlighted/underlined/marked) 2. A ___ of hope remained. (shred/glimmer/piece/bit) 3. He was ___ with pride. (beaming/glowing/shining/radiating) 4. The news was a bitter ___ to swallow. (pill/medicine/task/food) 5. She has a ___ for detail. (knack/eye/gift/talent) 6. The situation was fraught ___ danger. (with/of/by/to)."
    ),
    "C2": (
        "Description: Proficiency level. Can understand with ease virtually everything heard or read. Can summarise information from different sources. Can express him/herself spontaneously, very fluently and precisely. "
        "Vocabulary Focus: Complete mastery of sophisticated vocabulary, subtle nuances, synthesis of complex information. "
        "Sentence Examples: 'The sheer magnitude of the discovery was staggering.', 'Lest the message be misunderstood, it was repeated.' "
        "Task Difficulty: Professional/Native. Tasks involve synthesizing diverse information, extremely complex sentence structures, and absolute precision in meaning. "
        "Example Task (Advanced Synthesis): Rewrite the following complex sentences into a single coherent paragraph using sophisticated connectors: 1. The company's profits have declined. 2. This is due to market saturation. 3. New competitors have entered the field. 4. The board of directors is considering a merger. 5. This merger might save the firm. 6. Employees are worried about their jobs."
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
