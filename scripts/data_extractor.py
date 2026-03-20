import sys
import os
import tkinter as tk
from tkinter import filedialog
import easyocr
from backend.app.services.ai_service import AiService

class DataExtractor:
    def __init__(self):
        self.ai_service = AiService()

    def extract_data(self, file_path):
        reader = easyocr.Reader(['en', 'pl'])
        result = reader.readtext(file_path)

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
                            "id":        " ", #unikalny identyfikator 
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

        """

        response = self.ai_service.ask_local_with_photo(prompt, file_path)
        return response.get("message", response)




def main():
    root = tk.Tk()
    root.withdraw()

    extractor = DataExtractor()

    file_path = filedialog.askopenfilename(
        title="Wybierz zdjęcie",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    
    if not file_path:
        print("Nie wybrano pliku.")
        return

    print(f"Wybrano plik: {file_path}")
    print("Inicjalizacja AiService...")
    
    try:
        ai_service = AiService()
    except Exception as e:
        print(f"Błąd inicjalizacji AiService: {e}")
        return
        
    print("Wysyłanie zapytania do modelu...")
    
    try:
        response = extractor.extract_data(file_path)
        print("\nOdpowiedź modelu:")
        print(response)
    except Exception as e:
        print(f"Błąd podczas odpytywania modelu: {e}")

if __name__ == "__main__":
    main()