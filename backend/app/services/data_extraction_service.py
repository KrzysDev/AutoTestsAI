import json
import hashlib
from typing import Literal
from enum import Enum
from backend.app.services.ai_service import AiService
from backend.app.services.chunking_service import ChunkingService
from backend.app.models.schemas import Chunk, ChunkMetadata
import sys

class ExtractionType(Enum):
    cloud = 1
    local = 2

class DataExtractionService:
    def __init__(self):
        self.ai_service = AiService()
        self.chunking_service = ChunkingService()
        self.existing_subjects = []

    def extract_data(self, section: Literal["vocab", "gram"], language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], photo_path: str = None, extraction_type: ExtractionType = ExtractionType.cloud):
        if section == "vocab":
            return self.__extract_vocab(language, level, photo_path, extraction_type)
        elif section == "gram":
            return self.__extract_gram(language, level, photo_path)

    def __extract_vocab(self, language: Literal["en", "de"], level: Literal["A1", "A2", "B1", "B2", "C1", "C2"], photo_path: str = None, extraction_type: ExtractionType = ExtractionType.cloud) -> list[Chunk]:
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
                    Lista: {"pusta - to pierwszy chunk" if len(self.existing_subjects) == 0 else self.existing_subjects}
            - wszystkie pola subject powinny być zapisane małymi literami w WYŁĄCZNIE języku angielskim.
            - pole content to treść słownictwa. Jego format MUSI wyglądać następująco:
                <słowo po {"ANGIELSKU" if language == "en" else "NIEMIECKU"} - <tłumaczenie słowa w języku POLSKIM (z tekstu)> - <przykładowe zdanie z tym słowem w języku {"ANGIELSKIM" if language == "en" else "NIEMIECKIM"} (stworzone przez Ciebie)>  

            ##WYMAGANY FORMAT ODPOWIEDZI
            - Zwróć wyłącznie JSON. Nie dodawaj żadnych dodatkowych komentarzy ani tekstu. Nic nie może znaleźć się przed ani po JSONIE - zwracasz jedynie czysty JSON.
            - ignoruj śmieciowe nagłówki i znaki takie jak numery stron, podnagłówki (verbs, nouns, adjectives itp.)
            - ABSOLUTNIE NIC NIE MOZE ZNAJDOWAC SIE PRZED ANI PO JSONIE

        """

        if extraction_type == ExtractionType.cloud:
            answer = self.ai_service.ask_ollama_cloud_with_photo(prompt, photo_path)
        elif extraction_type == ExtractionType.local:
            answer = self.ai_service.ask_ollama_local_with_photo(prompt, photo_path)

        print("Debug Model Response: ")
        print(answer)
        print("\n")

        try: 
            data = json.loads(answer)
        except json.JSONDecodeError:
            raise ValueError(f"Model returned invalid JSON")
            sys.exit(1)

        if(data[0]["subject"]) not in self.existing_subjects:
            self.existing_subjects.append(data[0]["subject"])
        
        big_chunk = Chunk(
            id=hashlib.md5(data[0]["content"].encode()).hexdigest(),
            section="vocabulary",
            language=language,
            level=level,
            metadata=ChunkMetadata(
                subject=data[0]["subject"],
                content=data[0]["content"]
            )
        )
        
        chunks = self.chunking_service.chunk_data(big_chunk)

        for chunk in chunks:
            chunk.id = f"vocab-{hashlib.md5(chunk.metadata.content.encode()).hexdigest()[:8]}"

        return chunks

    def __extract_gram(self, text: str):
        pass
        
