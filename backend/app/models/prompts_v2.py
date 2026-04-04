from backend.app.models.schemas import RetrivedChunk, Group, Question
from typing import Literal


class SystemPrompts:
    def __init__(self):
        pass

    def get_queries_prompt(
        self,
        language: Literal["en", "de"],
        level: Literal["A1", "A2", "B1", "B2", "C1", "C2"],
        topic: str,
    ) -> str:
        example_content = {
            "en": '["Present Simple", "traveling vocabulary", "traveling]',
            "de": '["Präsens Verwendung und Tagesablauf Beispiele", "Wortschatz Verkehrsmittel und Pendeln", "Sehenswürdigkeiten in Berlin Texte"]'
        }

        return f"""
            ## TWOJA ROLA
            Jesteś ekspertem edukacyjnym i inżynierem promptów RAG dla języka: {language}.
            
            ## KONTEKST TEMATYCHNY (PODRĘCZNIK)
            Twoje zapytania o słówka powinny głównie skupić się na:
            - CZŁOWIEK, MIEJSCE ZAMIESZKANIA, PRACA, ŻYCIE PRYWATNE, ŻYWIENIE, ZAKUPY I USŁUGI, PODRÓŻOWANIE I TURYSTYKA, KULTURA, SPORT, NAUKA I TECHNIKA, PAŃSTWO I SPOŁECZEŃSTWO.

            ## ZADANIE
            Stwórz listę 3-5 zapytań (search queries) do bazy wektorowej w celu znalezienia materiałów do testu językowego.
            
            ## DANE WEJŚCIOWE
            - Język docelowy: {language}
            - Poziom biegłości: {level}
            - Temat/Słowa kluczowe: {topic}
            
            ## ZASADY TWORZENIA ZAPYTAŃ
            1. Rozbij temat na: gramatykę, słownictwo oraz kontekst sytuacyjny/kulturowy.
            2. Twórz zapytania jako naturalne frazy lub krótkie zdania (np. "How to describe a room in {language}") – unikaj pojedynczych słów kluczowych.
            3. Dopasuj styl zapytań do poziomu {level} (używaj struktur charakterystycznych dla tego poziomu).
            4. BEZWZGLĘDNIE wygeneruj zapytania w języku: {language}.
            
            ## WYJŚCIE
            Zwróć WYŁĄCZNIE surową listę JSON (tablica stringów). 
            Nie używaj znaczników markdown, bloków kodu ani wstępów.
            
            Przykład poprawnego wyjścia dla języka {language}:
            {example_content[language]}
            """.strip()

    def get_plan_test_creation_prompt(
        self,
        language: Literal["en", "de"],
        level: Literal["A1", "A2", "B1", "B2", "C1", "C2"],
        topic: str,
        retrieved_chunks: list[RetrivedChunk],
        group_count: int,
    ) -> str:
        return f"""
        ## TWOJA ROLA
        Jesteś ekspertem edukacyjnym, specjalizującym się w materiałach i testach dla języka {"angielskiego" if language == "en" else "niemieckiego"}.

        ## DANE WEJŚCIOWE
        - Język materiałów docelowych: {language}
        - Poziom trudności: {level}
        - Tematyka: {topic}
        - Liczba grup do zaplanowania: {group_count}
        - Znalezione fragmenty: {retrieved_chunks}

        ## TWOJE ZADANIE
        Twoim zadaniem jest stworzenie planu tworzenia sprawdzianu, który uwzględni prośbę nauczyciela oraz wszystkie inne podane wyżej wytyczne i dane z bazy danych.
        Stwórz opis w punktach tak, aby model AI który po tobie będzie ten test generował stworzył go jak najlepiej oddając intencje nauczyciela.
        Pamiętaj że sprawdzian będzie miał dokładnie {group_count} grup – zaplanuj strukturę każdej z nich.

        ## WYJŚCIE
        - Zwróć jedynie plan w punktach i nic więcej.
        - Plan musi być czytelny i łatwy w interpretacji.
        - Plan musi być szczegółowy, ale zmieść się maksymalnie w 1000 słowach.
        """

    def get_test_creation_prompt(
        self,
        language: Literal["en", "de"],
        level: Literal["A1", "A2", "B1", "B2", "C1", "C2"],
        topic: str,
        plan: str,
    ) -> str:
        return f"""
        ## TWOJA ROLA
        Jesteś ekspertem edukacyjnym, specjalizującym się w materiałach i testach dla języka {"angielskiego" if language == "en" else "niemieckiego"}.

        ## DANE WEJŚCIOWE
        - Język materiałów docelowych: {language}
        - Poziom trudności: {level}
        - Tematyka: {topic}
        - Plan tworzenia sprawdzianu: {plan}

        ## TWOJE ZADANIE
        Twoim zadaniem jest stworzenie pierwszej grupy sprawdzianu na podstawie podanego planu.
        Musisz jak najlepiej oddać intencje nauczyciela oraz wykonać grupę zgodnie z planem.

        ## WYJŚCIE
        - Zwróć grupę w formacie JSON zgodnym z poniższym schematem:
        {Group.model_json_schema()}
        - Nie zwracaj absolutnie nic poza tym schematem.
        - Nie wolno ci pisać żadnych znaków poprzedzających (markdown) ani następujących po JSON, takich jak ```json ani ```.
        - Niech sprawdzian ma nie mniej niz 20 pytań.
        -jedno question powinno sie skladac z wielu podpunkow. Jedno pytanie powinno miec conajmniej 3 podpunkty. Nie dopusc do sytuacji gdzie jest zadanie1-jednozdanie-zadanie2-jednozdanie itp. Musi byc wiecej podpunktow w jednym zadaniu ABSOLUTNIE NIE TYLKO JEDEN.
        -gdy jestes zapytany o czytanie ze zrozumieniem wymysl tekst na przynajmniej 300 slow (rozmiar rozprawki) nastepnie wymysl do niego odpowiedzi ABC. Mozesz tez stworzyc zadanie, w ktorym trzeba dopasowac nagłówek do danego tekstu.
        """

    def get_another_group_prompt(
        self,
        language: Literal["en", "de"],
        level: Literal["A1", "A2", "B1", "B2", "C1", "C2"],
        topic: str,
        plan: str,
        previous_group: Group,
    ) -> str:
        return f"""
        ## TWOJA ROLA
        Jesteś ekspertem edukacyjnym, specjalizującym się w materiałach i testach dla języka {"angielskiego" if language == "en" else "niemieckiego"}.
        Jesteś właśnie w trakcie tworzenia kolejnej grupy do swojego sprawdzianu.

        ## DANE WEJŚCIOWE
        - Język materiałów docelowych: {language}
        - Poziom trudności: {level}
        - Tematyka (prośba nauczyciela): {topic}
        - Plan sprawdzianu: {plan}
        - Poprzednia grupa (nie powtarzaj tych zadań): {previous_group}

        ## TWOJE ZADANIE
        Twoim zadaniem jest stworzenie kolejnej grupy do sprawdzianu zgodnie z planem.
        Zainspiruj się poprzednią grupą pod względem stylu, ale stwórz zupełnie nowe zadania – nie powtarzaj pytań ani słownictwa z poprzedniej grupy.

        ## WYJŚCIE
        - Zwróć grupę w formacie JSON zgodnym z poniższym schematem:
        {Group.model_json_schema()}
        - Nie zwracaj absolutnie nic poza tym schematem.
        - Nie wolno ci pisać żadnych znaków poprzedzających (markdown) ani następujących po JSON, takich jak ```json ani ```.
        -postaraj sie zachowac ogolny koncept poprzedniej grupy ale nie powtarzaj zadan.
        """