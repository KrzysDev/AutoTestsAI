import json
from typing import Literal
from backend.app.services.ai_service import AiService
from backend.app.services.chunking_service import ChunkingService
import hashlib
from backend.app.models.schemas import Chunk, ChunkMetadata


class DataExtractionService:

    def __init__(self):
        self.ai_service = AiService()
        self.chunking_service = ChunkingService()
        self.existing_subjects = []

    def extract_data(self, text: str, section : Literal["vocab", "gram"], language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]):
        if section == "vocab":
            return self.__extract_vocab(text, language, level)
        elif section == "gram":
            return self.__extract_gram(text, language, level)

    def __extract_vocab(self, text: str, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], photo_path: str = None) -> list[Chunk]:
        prompt = f"""
            ##TWOJE ZADANIE
            Jesteś ekspertem w dziedzinie języka {"angielskiego" if language == "en" else "niemieckiego"}
            Twoim zadaniem jest wyciągnięcie z podanego tekstu z podręcznika słownictwa i uporządkowanie go w odpowiednim formacie.

            ##WAŻNE
            MUSISZ wydobyć ABSOLUTNIE WSZYSTKIE słówka i zwroty, jakie znajdziesz w podanym tekście. Nie pomijaj ani jednego słowa, nie używaj skrótów typu "itd", "itp". To krytyczne dla sukcesu zadania aby niczego nie pominąć!

            ##WYMAGANY FORMAT
            Twój wymagany format odpowiedzi to JSON wyglądający w następujący sposób:
                {{
                    "subject": "temat",
                    "content": "treść"
                }}

            ##WYMAGANIA ODPOWIEDNIEGO FORMATU JSON:
            - pole subject to miejsce które określa temat słownictwa. Przykłady to: "education", "place of residence", "work" czy także "private life".
            - podany temat możesz zauważyć w wysłanym ci tekście. Prawdopodobnie jest nagłówkiem.
            - Nie zwracaj uwagi na nagłówki nieodnoszące się do treści słownictwa takie jak "Lista słownictwa".
            - pole subject powinno zawierać identyczne tematy (jeśli się powtarzają). Z tego powodu:
                - jeżeli poniższa lista NIE jest pusta wykorzystaj stworzone przez ciebie już tematy i nie twórz synonimów. Np dla jeżeli na podanej liście znajduje się "nature" nie pisz "enviorement" tylko "nature".
                    Lista: {"pusta" if len(self.existing_subjects) == 0 else self.existing_subjects}
            - wszystkie pola subject powinny być zapisane małymi literami w WYŁĄCZNIE języku angielskim.
            - pole content to treść słownictwa. Jego format MUSI wyglądać następująco:
                <słowo po {"ANGIELSKU" if language == "en" else "NIEMIECKU"} - <tłumaczenie słowa w języku POLSKIM (z tekstu)> - <przykładowe zdanie z tym słowem w języku {"ANGIELSKIM" if language == "en" else "NIEMIECKIM"} (stworzone przez Ciebie)>  

            ##TEKST Z PODRECZNIKA
            {text}

            ##WYMAGANY FORMAT ODPOWIEDZI
            - Zwróć wyłącznie JSON. Nie dodawaj żadnych dodatkowych komentarzy ani tekstu. Nic nie może znaleźć się przed ani po JSONIE - zwracasz jedynie czysty JSON.
            - ignoruj śmieciowe nagłówki i znaki takie jak numery stron, podnagłówki (verbs, nouns, adjectives itp.)
            - ABSOLUTNIE NIC NIE MOZE ZNAJDOWAC SIE PRZED ANI PO JSONIE

        """

        answer = self.ai_service.ask_cloud_with_photo(prompt, photo_path)

        print("Debug Odpowiedz Modelu: ")
        print(answer['message'])
        print("\n")

        try: 
            data = json.loads(answer['message'])
        except json.JSONDecodeError as e:
            raise ValueError(f"Model returned invalid JSON: {e}")
        
        big_chunk = Chunk(
            id=hashlib.md5(data["content"].encode()).hexdigest(),
            section="vocab",
            language=language,
            level=level,
            metadata=ChunkMetadata(
                subject=data["subject"],
                content=data["content"]
            )
        )
        
        chunks = self.chunking_service.chunk_data(big_chunk)

        for chunk in chunks:
            chunk.id = f"vocab-{hashlib.md5(chunk.metadata.content.encode()).hexdigest()[:8]}"

        return chunks

    def __extract_gram(self, text: str):
        pass
        
