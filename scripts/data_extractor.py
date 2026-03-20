import sys
import os
import tkinter as tk
from tkinter import filedialog

from backend.app.services.ai_service import AiService

class DataExtractor:
    def __init__(self):
        self.ai_service = AiService()

    def extract_data(self, file_path):
        prompt = """
        #ZADANIE
        Musisz wyeksportować dane z przesłanych ci zdjęć. Są to zdjęcia podreczników z języka angielskiego.
        Gdy zobaczysz słówka, zapisz je jako listę. Gdy zobaczysz definicję gramatyki (np. czas Present Simple z języka angielskiego) zapisz jej definicję, przykłady oraz 
        wszystko to co znajdziesz w podręczniku.

        #WYMAGANIA
        - Odpowiedź musi być w języku polskim,
        - Odpowiedź musi być w formacie JSON, dokładnie takim, jaki zostanie przedstawiony poniżej. Nie dodawaj niczego przed oraz po JSONie.
        {
            "id":        " ", #unikalny identyfikator 
            "section":   " ", #nazwa sekcji np. vocabulary lub grammar
            "language":  " ", #język                  
            "level":     " ", #poziom np. B2, B1, C2, C1 itp.                    
            
            "metadata" : {
                "subject" : "",  #temat np - środowisko, życie w mieście, technologia, zawody i przyszłość, oświata itp. (Temat często podany jest na samej górze strony w podręczniku)    
                "content": " ", #zawartość chunka - dla gramatyki (grammar) bedzie to część jakiejś definicji (np. Present Simple używamy gdy...) natomiast dla słówek (vocabulary) - fragment listy słówek.
                #Dla każdego słówka z listy słówek postaraj się zawrzeć po przykladzie użycia go w zdaniu.
            }
        }

        
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