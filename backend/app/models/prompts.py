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
                "sections info": """wypisz wszystkie typy zadań, jakie mają pojawić się w teście. Określ ich typ (section_type) (np. vocabulary), temat (subject) (np. present_simple, reading etc. — JEDNO słowo lub fraza, nigdy dwa tematy naraz) oraz ilość wystąpień (amount). Każde pole może mieć tylko jedną wartość.
                subject musi być DOKŁADNIE jedną z tych wartości:
                Present Simple, Past Simple, Present Continuous, Past Continuous, 
                Present Perfect, Future Simple.
                Section_type moze byc JEDYNIE: vocabulary, reading, listening, writing, grammar - zadnych innych wartosci. 
                Nigdy nie używaj innych wartości jak 'reading_comprehension' czy 'tense_review'""",
                "total tasks info" : "określ łączną liczbę zadań na podstawie zapytania nauczyciela",
                "output rule info" : "Zwróć WYŁĄCZNIE poprawny JSON. Bez tekstu przed ani po. Bez markdown. Bez ```" 
            },
            "pytanie nauczyciela": topic,
            "wymagany format json": {
                "task": "",
                "level": "A1|A2|B1|B2|C1|C2",
                "target_age": "kids|teens|adults",
                "sections": [
                    {
                        "section_type": "grammar",
                        "subject": "present_simple",
                        "amount": 3
                    }
                ],
                "total_tasks": 3
            }
        }
        return json.dumps(structure, ensure_ascii=False, indent=2)

    def get_section_generation_prompt(
        self,
        data: RetrievalData,
        teacher_request: str,
        previous_summaries: list[str] | None = None
    ) -> str:

        # Budujemy blok zakazanych treści
        if previous_summaries:
            forbidden_block = (
                "UWAGA — PONIŻSZE TREŚCI ZOSTAŁY JUŻ UŻYTE W POPRZEDNICH ZADANIACH. "
                "ABSOLUTNIE NIE WOLNO CI ICH POWTARZAĆ — ani tych samych zdań, ani tych samych sytuacji, "
                "ani tych samych słów kluczowych. Wymyśl zupełnie inne konteksty i przykłady.\n\n"
                + "\n\n---\n\n".join(
                    f"Zadanie {i + 1}:\n{s}" for i, s in enumerate(previous_summaries)
                )
            )
        else:
            forbidden_block = "To pierwsze zadanie — brak poprzednich."

        structure = {
            "twoja_rola": (
                "Jesteś ekspertem w tworzeniu materiałów dydaktycznych do nauki języków obcych. "
                "Twoim zadaniem jest stworzenie JEDNEGO zadania na podstawie dostarczonych danych."
            ),
            "zasady_ogolne": [
                "Wzoruj się na przykładowych zadaniach z sekcji 'dane_z_retrival' pod względem poziomu i konstrukcji.",
                "Zwróć WYŁĄCZNIE JSON w wymaganym formacie. Zero tekstu przed ani po. Zero markdown (bez ```json, bez ```).",
                "Używaj WYŁĄCZNIE podwójnych cudzysłowów (\") — nigdy pojedynczych (').",
                "Nie kopiuj gotowych zdań z przykładów — twórz nowe, oryginalne treści."
            ],
            "prosba_nauczyciela": teacher_request,
            "dane_z_retrival": {
                "Grammar_Instructions": [chunk.model_dump() for chunk in data.instructions.grammar_instructions],
                "Exercise_Instructions": [chunk.model_dump() for chunk in data.instructions.exercise_instructions]
            },
            "ZAKAZ_POWTARZANIA_uzyte_tresci": forbidden_block,
            "wymagany_format_json": {
                "Question": {
                    "content": {
                        "instruction": "<tutaj napisz polecenie do zadania>",
                        "body": "<tutaj napisz treść zadania — zdania, tekst, pytania itp.>"
                    }
                }
            }
        }

        return json.dumps(structure, ensure_ascii=False, indent=2)