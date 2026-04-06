import json

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
                        "type": "vocabulary",
                        "subject": "Present Simple",
                        "amount": 3
                    }
                ],
                "total_tasks": "<liczba calkowita, okreslajaca ile zadan lacznie ma byc w tescie>"
            }
        }
        return json.dumps(structure, ensure_ascii=False, indent=2)