import sys
import os
import tkinter as tk
from tkinter import filedialog

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.services.ai_service import AiService

class DataExtractor:
    def __init__(self):
        self.ai_service = AiService()

    def extract_data(self, file_path):
        prompt = "Co znajduje się na tym zdjęciu? Opisz to krótko."
        response = self.ai_service.ask_local(prompt, file_path)
        return response.get("message", response)




def main():
    root = tk.Tk()
    root.withdraw()

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
        
    prompt = "Co znajduje się na tym zdjęciu? Opisz to krótko."
    print("Wysyłanie zapytania do modelu...")
    
    try:
        response = ai_service.ask_local(prompt, file_path)
        print("\nOdpowiedź modelu:")
        print(response.get("message", response))
    except Exception as e:
        print(f"Błąd podczas odpytywania modelu: {e}")

if __name__ == "__main__":
    main()
