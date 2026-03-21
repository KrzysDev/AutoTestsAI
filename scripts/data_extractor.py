import sys
import os
import tkinter as tk
from tkinter import filedialog
import easyocr
from backend.app.services.ai_service import AiService
import time

import json

class DataExtractor:
    def __init__(self):
        self.ai_service = AiService()
        self.reader = easyocr.Reader(['en', 'pl'])
        self.previous_sections = []

    def extract_data(self, file_path):
        result = self.reader.readtext(file_path)

        extracted_text = ""
        for _, text, _ in result:
            extracted_text += text + "\n"
        
        prompt = f"""

                #ZADANIE
                Musisz wyeksportować i uporzadkowac dane wyciągnięte ze zdjęcia przez silnik OCR. Zdjęcia pochodzą z podreczników z języka angielskiego.
                Gdy zobaczysz słówka, zapisz je jako listę. Gdy zobaczysz definicję gramatyki (np. czas Present Simple z języka angielskiego) zapisz jej definicję, przykłady oraz 
                wszystko to co najważniejsze znalazło się w wyeksportowanym ze zdjęcia tekście.

                #KONTEKST
                Wyeksportowany tekst:
                {extracted_text}

                #WYMAGANIA
                - Odpowiedź musi być w języku polskim.
                - Odpowiedź musi być w formacie JSON. Struktura przedstawiona poniżej (musi być dokładnie odwzorowana):
                        {{
                            "id":        " ", #pozostaw puste 
                            "section":   " ", #nazwa sekcji np. vocabulary lub grammar (tylko te dwie wchodza w grę)
                            "language":  " ", #język                  
                            "level":     " ", #poziom np. B2, B1, C2, C1 itp. UWAGA - Wybierz TYLKO JEDEN. Nie moze byc np. B2/C1.                     
                            
                            "metadata" : {{
                                "subject" : "",  #temat np - środowisko, życie w mieście, technologia, zawody i przyszłość, oświata itp. (Temat często podany jest na samej górze strony w podręczniku)
                                "content": " ", #zawartość chunka - dla gramatyki (grammar) bedzie to część jakiejś definicji (np. Present Simple używamy gdy...) natomiast dla słówek (vocabulary) - fragment listy słówek.
                                #Dla każdego słówka z listy słówek postaraj się zawrzeć po przykladzie użycia go w zdaniu.
                            }}
                        }}
                - Twojej odpowiedzi pod żadnym pozorem nie może być nic poza JSONem. Zarówno przed jak i po strukturze JSONa. Nie dodawaj zadnych komentarzy, nie dodawaj zadnych dodatkowych informacji. Po prostu czysty JSON.
                - pomiń nagłówki i inne niepotrzebne informacje takie jak numer strony, lub podrozdzialy w tekscie ze slowkami (np. verbs, adjectives, nouns itp.)
                - zwracaj uwagę na nagłówki, które coś wnoszą do tekstu np. temat słówek, temat gramatyki itp.
                - Pola sections muszą być konsekwentne. Jeśli słówka dotyczą działu 'nature', ale w liście poprzednich sections pojawiło się słowo 'enviorment' to użyj słowa 'enviorment'. Nie twórz synonimów.

                #LISTA UTWORZONYCH SEKCJI PONIŻEJ 
                Jeżeli nic sie nie znajduje niżej, pomiń to:
                {self.previous_sections}
        """

        words = prompt.split()

        tokens = int(len(words) * 2.5)

        start_time = time.time()

        response = self.ai_service.ask_cloud(prompt)

        if response['section'] not in self.previous_sections:
            self.previous_sections.append(response['section'])

        

        end_time = time.time()

        elapsed_time = end_time - start_time
        
        print(f"🤖 Wygenerowano w {elapsed_time} sekund")
        print(f"🤖 Przetworzono {tokens} tokenów")

        return response.get("message", response)




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
            print("Odpowiedź modelu:")
            all_responses.append(response)
            images_processed += 1
            os.system("cls")
            
        except Exception as e:
            print(f"Błąd podczas odpytywania modelu dla pliku {filename}: {e}")
    
    
        

if __name__ == "__main__":
    main()