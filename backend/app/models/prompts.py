
from typing import Literal
import json
from backend.app.models.schemas import Test, Chunk

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
    def get_query_requests_prompt(self, plan: str) -> str:
        return f"""
            ##ZADANIE
            Na podstawie podanego planu, wygeneruj zapytania do modelu językowego.

            ##CO ZWRACASZ
            Liste zapytan do systemu wyszukujacego materialy do testu. Niech zapytania beda sformulowane tak aby jak najwieksza szansa byla na odnalezienie przydatnych chunków.
            Kazde zapytanie powinno byc wlasnym zdaniem w nowej linii.

            ##Przyklad Odpowiedzi:
                ' - Present Simple
                  - czlowiek słówka / człowiek
                  - dom i rodzina '
            

            ##PLAN:
            {plan}

            ##UWAGI
            -zauwaz ze "zdania" w przykladzie to same proste hasla, nie zdania poprawne skladniowo. takie wlasnie hasla, najlepiej pojedyczne slowa chce zebys wypisal pod soba
            -nie zwracaj nic poza listą zapytań. NIC POZA TYM.
            -lista zapytań ma być czytelna i prosta do zrozumienia.
            -lista zapytań ma byc zdaniami (MAKSYMALNIE 4)
            -kazde zdanie musi byc oddzielone znakiem nowej linii (innymi slowy kazde ma byc w innej linii)
        """
    def get_test_generation_prompt(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], data: list[Chunk], plan :str, teachers_request: str, group_count: int, question_count: int) -> str:
        return f"""
            ##CECHY
            Jesteś specjalistą od układania testów językowych z języka {"angielskiego" if language == "en" else "niemieckiego"} na poziomie {level}. Będziesz zajmowaniem się układaniem testów na podstawie przesłanego ci kontekstu oraz prośby nauczyciela w odpowiednim formacie JSON.

            ##PROŚBA NAUCZYCIELA
            {teachers_request}

            ##ULOZONY PRZEZ CIEBIE PLAN DZIALANIA W UKLADANIU TESTU
            {plan}

            ##DANE WYCIAGNIETE Z JEZYKOWEJ BAZY DANYCH
            {data}

            ##ILOSC GRUP DO STWORZENIA
            {group_count}

            ##ILE PYTAN W JEDNEJ GRUPIE:
            {question_count}

            ##WYMAGANA STRUKTURA JSON
            {json.dumps(Test.model_json_schema(), indent=2)}
 
        """

    def get_test_validation_prompt(self, s: str) -> str:
        return f"""
            ##ZADANIE
            Sprawdz poprawnosc testu. 

            ##TEST DO SPRAWDZENIA
            {s}

            ##UWAGI
            -nie zwracaj nic poza poprawnym testem. NIC POZA TYM.
            -test ma byc poprawny i spelniac wszystkie wymagania takie jak odpowiednia struktura json:
            {json.dumps(Test.model_json_schema(), indent=2)}

            -ZWROC JEDYNIE TEST W POPRAWNEJ WERSJI JSON ZADEN TEKST NIC POZA TYM.
        """
    def get_general_question_prompt(self, topic: str) -> str:
        return f"""
            ##ZADANIE
            Na podstawie podanego zapytania nauczyciela, odpowiedz na nie.

            ##ZAPYTANIE NAUCZYCIELA:
            {topic}

            ##TWOJE CECHY
            -Jesteś specjalistą od tworzenia testów językowych dla uczniów na różnym poziomie zaawansowania.
            -Potrafisz tworzyc testy wyłącznie z języka angielskiego.
            -Jesli uznasz to za konieczne, wspomnij ze jestes Asystentem w wersji testowej i że nie potrafisz zrobić bardziej zaawansowanych testów dobrze. Tj. Sluchanie ze zrozumieniem.
            -odpowiadaj w takim samym języku jak zapytanie nauczyciela.
        """