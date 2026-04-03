
from typing import Literal

class SystemPrompts:

    def get_data_extraction_prompt(self, language: Literal["en", "de"]) -> str:
        return f"""
                ##ZADANIE
                Z podanego zdjecia podrecznika do jezyka {"angielskiego" if language == "en" else "niemieckiego"} wypisz WSZYSTKIE wystepujace tam slowka w podanym formacie JSON:

                ##POPRAWNY FORMAT JSON
                {{
                "subject": temat, który twoim zdaniem najlepiej pasuje wybrany z tych: human being, place of residence, education, work, private life, nutrition, shopping and services, travel and tourism, culture, sport, health, science and technology, state and society.  
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
    def get_grammar_extraction_prompt(self, language: Literal["en", "de"]) -> str:
        return f"""
            ##ZADANIE
            Zapoznaj sie z zagadnieniem gramatycznym znajdujacym sie na podanym zdjeciu podrecznika do jezyka {"angielskiego" if language == "en" else "niemieckiego"}. Przenalizuj zasady, wystepowanie oraz przykłady.

            ##POPRAWNY FORMAT JSON
            {{
                "subject": temat, który twoim zdaniem najlepiej pasuje (nazwa czasu / kategorii gramatycznej)
                "content":
                {{
                    "description": "opis zagadnienia gramatycznego (po polsku)",
                    "examples": [
                        "example 1 (po angielsku)",
                        "example 2 (po angielsku)",
                        "example 3 (po angielsku)"
                    ]
                }}
            }}

            ##UWAGI
            -nie zwracaj nic poza JSON'em. NIc nie moze znajdować się przed ani po nim. Sam czysty json. Nie poprzedzaj go znakami takimi jak ``` lub innymi
            -jeżeli na podanym zdjęciu znajdują się przykłady użycia danego zagadnienia (np. czasu, gramatycznej struktury) to przepisz je do pola "examples" w JSON'ie
            -jeżeli na podanym zdjęciu nie znajdują się przykłady użycia danego zagadnienia (np. czasu, gramatycznej struktury) to pole wymyśl własne przykłady.
        """

    def get_data_correction_prompt(self, language: Literal["en", "de"], extracted_data) -> str:
        return f"""
            ##ZADANIE
            Podany JSON, popraw tak aby spełniał poniższe warunki. 

            ##POPRAWNY FORMAT JSON
            {{
                "subject": temat, który twoim zdaniem najlepiej pasuje wybrany z tych: human being, place of residence, education, work, private life, nutrition, shopping and services, travel and tourism, culture, sport, health, science and technology, state and society.  
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
    def get_data_grammar_correction_prompt(self, language: Literal["en", "de"], extracted_data) -> str:
        return f"""
            ##ZADANIE
            Podany JSON (lub zły tekst), popraw tak aby spełniał poniższe warunki.

            ##POPRAWNY FORMAT JSON
            {{
                "subject": temat, który twoim zdaniem najlepiej pasuje (nazwa czasu / kategorii gramatycznej)
                "content":
                {{
                    "description": "opis zagadnienia gramatycznego (po polsku)",
                    "examples": [
                        "example 1 (po angielsku)",
                        "example 2 (po angielsku)",
                        "example 3 (po angielsku)"
                    ]
                }}
            }}

            ##UWAGI
            -nie zwracaj nic poza JSON'em. NIc nie moze znajdować się przed ani po nim. Sam czysty json. Nie poprzedzaj go znakami takimi jak ``` lub innymi
            -jeżeli na podanym zdjęciu znajdują się przykłady użycia danego zagadnienia (np. czasu, gramatycznej struktury) to przepisz je do pola "examples" w JSON'ie
            -jeżeli na podanym zdjęciu nie znajdują się przykłady użycia danego zagadnienia (np. czasu, gramatycznej struktury) to pole wymyśl własne przykłady.

            #DANE DO POPRAWY
            {extracted_data}
        """
    def get_classification_prompt(self, text: str) -> str:
        return f"""
            ##ZADANIE
            Na podstawie podanego tekstu musisz okreslic czy jest to ogólne zapytanie czy prośba o utworzenie testu/sprawdzianu/kartkowki.

            #CO ZWRACASSZ
            -JEDYNIE - 'general' lub 'test'. NIC POZA TYM.

            #ZAPYTANIE DO ANALIZY
            {text}
        """

    def get_test_planning_prompt(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], topic: str) -> str:
        return f"""
            ##ZADANIE
            Na odstawie podanego zapytania nauczyciela, zaplanuj test.

            ##CO ZWRACASZ
            Czytelny, prosty do zrozumienia plan, który będzie instrukcją skoonstruowania testu krok po kroku tak jak nauczyciel prawdopodobnie sobie tego zyczy.
            Napisz liste kroków, przez która model językowy przechodząc, będzie tworzył odpowiedni dla nauczyciela test.

            ##ZAPYTANIE NAUCZYCIELA:
            {topic}

            ##DANE
            Język: {"angielski" if language == "en" else "niemiecki"}
            Poziom: {level}

            ##UWAGI
            -nie zwracaj nic poza planem. NIC POZA TYM.
            -plan ma być czytelny i prosty do zrozumienia.
            -plan ma być listą kroków, przez która model językowy przechodząc, będzie tworzył odpowiedni dla nauczyciela test.
        """