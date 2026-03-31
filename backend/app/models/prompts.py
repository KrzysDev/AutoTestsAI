
from typing import Literal

class SystemPrompts:

    def get_data_extraction_prompt(language: Literal["en", "de"]) -> str:
        return f"""
                ##ZADANIE
                Z podanego zdjecia podrecznika do jezyka {"angielskiego" if language == "en" else "niemieckiego"} wypisz WSZYSTKIE wystepujace tam slowka w podanym formacie JSON:

                ##POPRAWNY FORMAT JSON
                {{
                "content": [
                {{
                    "word" : ({"angielskie" if language == "en" else "niemieckie"} słowo),
                    "translation" : (polskie tlumaczenie)
                }},
                    ...... itd...
                ]
                }}

                ##UWAGI
                -nie zwracaj nic poza JSON'em. NIc nie moze znajdować się przed ani po nim. Sam czysty json. Nie poprzedzaj go znakami takimi jak ``` lub innymi
                -uzywaj tlumaczen podanych wylacznie na zdjeciu nie pisz swoich
        """

    def get_data_correction_prompt(language: Literal["en", "de"], extracted_data) -> str:
        return f"""
            ##ZADANIE
            Podany JSON, popraw tak aby spełniał poniższe warunki. 

            ##POPRAWNY FORMAT JSON
            {{
                "content": [
                {{
                    "word" : ({"angielskie" if language == "en" else "niemieckie"} słowo),
                    "translation" : (polskie tlumaczenie)
                }},
                    ...... itd...
                ]
            }}

            ##UWAGI
            -nie zwracaj nic poza JSON'em. NIc nie moze znajdować się przed ani po nim. Sam czysty json. Nie poprzedzaj go znakami takimi jak ``` lub innymi
            -uzywaj tlumaczen podanych wylacznie na zdjeciu nie pisz swoich
            -jeżeli jakieś tłumaczenie jest niepoprawne, popraw je
            -jeżeli jakieś słowo jest nieczytelne, źle napisane i nie wiesz czym jest usuń je.

            #DANE DO POPRAWY
            {extracted_data}
        """
