import json
from backend.app.models.schemas import GenerationPrompt, RetrivedChunk, TransformedPrompt, RetrievalData, RetrievalInstructions

class SystemPrompts:
    def __init__(self):
        pass

    def get_transform_request_to_prompt(self, topic: str):
        structure = {
            "twoja rola info": "Jesteś specjalistą od układania testów językowych. Twoim zadaniem jest przekształcenie poniższego zapytania nauczyciela w podany format JSON, tak aby model językowy czytający ten format wiedział, jak ma odwzorować test.",
            "zasady info": {
                "task info": "w tym polu należy streścić to, co napisał nauczyciel",
                "level info": "określ poziom CEFR (A1, A2, B1, B2, C1, C2) na podstawie zapytania nauczyciela",
                "target age info": "określ docelową grupę wiekową uczniów (np. kids, teens, adults)",
                "sections info": "wypisz wszystkie typy zadań, jakie mają pojawić się w teście. Określ ich typ(type) (np. vocabulary), temat (np. present simple, present contionous, reading etc. you have to pick one) oraz ilość ich wystąpień(amount) (wybierz dowolnie, chyba że została podana przez nauczyciela) każde pole może mieć tylko jedną wartość. Nie łącz wartości ze sobą. Np. Present Simple i Present Continous jako temat byłoby błędne",
                "total tasks info": "określ łączną liczbę zadań na podstawie zapytania nauczyciela",
                "output rule info": "nie zwracaj nic poza tym JSON (bez tekstu przed ani po, bez markdown, bez ```)"
            },
            "pytanie nauczyciela": topic,
            "wymagany format json": {
                "task": "",
                "level": "A1|A2|B1|B2|C1|C2",
                "target_age": "kids",
                "sections": [
                    {
                        "section_type": "vocabulary",
                        "subject": "Present Simple",
                        "amount": 3
                    }
                ],
                "total_tasks": "<liczba calkowita, okreslajaca ile zadan lacznie ma byc w tescie>"
            }
        }
        return json.dumps(structure, ensure_ascii=False, indent=2)

    def get_section_generation_prompt(self, data: RetrievalData, teacher_request: str) -> GenerationPrompt:
       structure = {
            "twoja rola": "Jesteś ekspertem w tworzeniu materiałów dydaktycznych do nauki języków obcych. Twoim zadaniem jest stworzenie jednego zadania na podstawie dostarczonych danych z retrivalu.",
            "zasady": "W polu 'dane z retrival' podane są przykładowe zadania na których MUSISZ się wzorować tworząc nowe podobnego rodzaju. Skup sie na poziomie jaki reprezentuja i jak są skoonstruowane. Poniżej znajdziesz też instrukcje w jaki sposób krok po kroku stworzyć tego typu zadanie. Musisz zwrócić wyłącznie JSON w wymaganym formacie. Nic więcej poza nim. Nie dodawaj nic przed ani po jsonie w tym znaków markdown takich jak ```json lub ```",
            "szczegóły_pół" : "level - poziom językowy CEFR (A1, A2, B1...C2), age_group - docelowa grupa wiekowa (kids, teens, adults), task_type - typ zadania (np. vocabulary, grammar, reading etc. musisz wybrac jeden), topic - temat zadania (np. present simple, present contionous, reading etc. musisz wybrac jeden), amount - ilość wystąpień / ile zadan musisz w tej liscie tego typu stworzyć (wybierz dowolnie, chyba że została podana przez nauczyciela)",
            "prosba_nauczyciela" : teacher_request,
            "dane z retrival": {
                "Instructions": {
                    "Grammar_Instructions": [chunk.model_dump() for chunk in data.instructions.grammar_instructions],
                    "Exercise_Instructions": [chunk.model_dump() for chunk in data.instructions.exercise_instructions]
                },
            },

            "wymagany format json": {
                "Question": {
                    "content": {
                        "instruction": "",
                        "body": ""
                    }
                }
            }
        }
       return str(structure)