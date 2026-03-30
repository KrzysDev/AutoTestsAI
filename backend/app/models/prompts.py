
from typing import Literal

class SystemPrompts:

    def get_data_extraction_prompt(language: Literal["en", "de"]) -> str:
        return f"""
                #ZADANIE
                Z podanego zdjecia podrecznika do jezyka {"angielskiego" if language == "en" else "niemieckiego"} wypisz WSZYSTKIE wystepujace tam slowka w podanym formacie JSON:

                {{
                "content": [
                {{
                    "word" : (polskie slowo),
                    "translation" : (tutaj polskie tlumaczenie)
                }},
                    ...... itd...
                ]
                }}

                #UWAGI
                -nie zwracaj nic poza JSON'em. NIc nie moze znajdować się przed ani po nim. Sam czysty json. Nie poprzedzaj go znakami takimi jak ``` lub innymi
                -uzywaj tlumaczen podanych wylacznie na zdjeciu nie pisz swoich
        """
