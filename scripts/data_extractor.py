import sys
import os
import tkinter as tk
from tkinter import filedialog
import easyocr
from backend.app.services.ai_service import AiService
import time
from backend.app.models.schemas import FlashcardChunk
import json
import re

class DataExtractor:
    def __init__(self):
        self.ai_service = AiService()
        self.reader = easyocr.Reader(['en', 'pl'])
        self.previous_voc_subjects = []
        self.previous_gram_subjects = []
    
    def parse_and_validate(self, raw: str) -> FlashcardChunk:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            raise ValueError(f"Model nie zwrócił JSON. Odpowiedź: {raw[:300]}")
        
        data = json.loads(match.group(), strict=False)

        if isinstance(data.get("metadata", {}).get("content"), list):
            items = data["metadata"]["content"]
            lines = []
            for item in items:
                if isinstance(item, dict):
                    lines.append(", ".join(f"{k}: {v}" for k, v in item.items()))
                else:
                    lines.append(str(item))
            data["metadata"]["content"] = "\n".join(lines)

        return FlashcardChunk.model_validate(data)

    def extract_data(self, file_path):
        result = self.reader.readtext(file_path)

        extracted_text = ""
        for _, text, _ in result:
            extracted_text += text + "\n"
        
        prompt = f"""
            # ROLA
            Jesteś ekspertem od przetwarzania danych edukacyjnych z podręczników do języka angielskiego.

            # ZADANIE
            Wyeksportuj i uporządkuj dane wyciągnięte ze zdjęcia przez silnik OCR.
            - Słówka → zapisz jako listę z przykładami użycia w zdaniu.
            - Gramatyka → zapisz definicję, zasady, przykłady i wyjątki.

            # TEKST Z OCR
            {extracted_text}

            # FORMAT ODPOWIEDZI
            Odpowiedz WYŁĄCZNIE poprawnym JSONem (bez komentarzy, bez tekstu przed/po):
            {{
                "id": "",
                "section": "<vocabulary|grammar>",
                "language": "<język>",
                "level": "<A1|A2|B1|B2|C1|C2>",
                "metadata": {{
                    "subject": "<temat>",
                    "content": "<treść jako string>"
                }}
            }}

            # ZASADY
            1. Odpowiedź w języku polskim.
            2. Pole "section" to TYLKO "vocabulary" albo "grammar".
            3. Pole "level" to JEDEN poziom (np. "B2"), nigdy kombinacja typu "B2/C1".
            4. Pole "content" MUSI być zwykłym stringiem (nie listą, nie obiektem JSON).
            - Dla słówek: lista słówek, każde z przykładem użycia w zdaniu.
            - Dla gramatyki: definicja, zasady, przykłady zdań.
            5. Pomiń: numery stron, podkategorie słówek (verbs, adjectives, nouns), śmieciowe nagłówki.
            6. Zwracaj uwagę na nagłówki zawierające temat (zwykle na górze strony w podręczniku).

            # KONSEKWENCJA TEMATÓW v1 (KRYTYCZNE)
            Pole "subject" MUSI być spójne z wcześniej użytymi tematami.
            Jeśli poniżej znajduje się lista już użytych tematów, MUSISZ wybrać z niej najbardziej pasujący temat zamiast tworzyć nowy synonim.
            Przykład: jeśli istnieje temat "environment", NIE twórz "nature" ani "ecology" — użyj "environment".
            Nowy temat twórz TYLKO gdy żaden z istniejących nie pasuje.

            # KONSEKWENCJA TEMATÓW v2 (KRYTYCZNE)
            Jeżeli tekst dotyczy gramatyki i nie widać wyraźnego nagłówka tematu, to najprawdopodobniej jest to kontynuacja ostatniego tematu gramatycznego. W takim przypadku użyj tego samego tematu.

            ## Dotychczasowe tematy słówek:
            {self.previous_voc_subjects if self.previous_voc_subjects else "(brak — to pierwszy chunk)"}

            ## Dotychczasowe tematy gramatyki:
            {self.previous_gram_subjects if self.previous_gram_subjects else "(brak — to pierwszy chunk)"}
        """

        start_time = time.time()

        raw_response = self.ai_service.ask_cloud(prompt)

        try:
            chunk = self.parse_and_validate(raw_response["message"])
        except (ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Błąd parsowania odpowiedzi dla {file_path}: {e}")

        subject = chunk.metadata.subject
        if chunk.section == "vocabulary" and subject not in self.previous_voc_subjects:
            self.previous_voc_subjects.append(subject)
        elif chunk.section == "grammar" and subject not in self.previous_gram_subjects:
            self.previous_gram_subjects.append(subject)

        end_time = time.time()
        print(f"🤖 Wygenerowano w {end_time - start_time:.2f} sekund")

        return chunk




def main():
    root = tk.Tk()
    root.withdraw()

    extractor = DataExtractor()

    directory_path = filedialog.askdirectory(
        title="Wybierz folder ze zdjęciami"
    )
    
    if not directory_path:
        print("Nie wybrano folderu.")
        return

    print(f"Wybrano folder: {directory_path}")

    file_name = input("Podaj nazwę pliku: ")
    
    image_files = [f for f in os.listdir(directory_path) if f.lower().endswith(('.jpg', '.png'))]
    
    if not image_files:
        print("Nie znaleziono plików .jpg ani .png w wybranym folderze.")
        return

    print(f"Znaleziono {len(image_files)} zdjęć do przetworzenia.")

    images_processed = 0
    all_responses = []

    for filename in image_files:
        file_path = os.path.join(directory_path, filename)
        print(f"\n--- Przetwarzanie pliku: {file_path} ---")
        
        try:
            print(f"processing images... {images_processed}/{len(image_files)}")

            response = extractor.extract_data(file_path)
            all_responses.append(response.model_dump())
            images_processed += 1
            
        except Exception as e:
            print(f"Błąd podczas odpytywania modelu dla pliku {filename}: {e}")
            images_processed += 1
    
    with open(f"C:\\Users\\USER\\Desktop\\moje rzeczy\\projekty\\inne\\TestGenerator\\data\\{file_name}.json", "w", encoding="utf-8") as f:
        json.dump(all_responses, f, ensure_ascii=False, indent=2)
    
    

if __name__ == "__main__":
    main()