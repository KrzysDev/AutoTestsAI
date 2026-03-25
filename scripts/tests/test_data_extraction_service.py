from backend.app.services.data_extraction_service import DataExtractionService

import tkinter as tk
from tkinter import filedialog

def main():
    service = DataExtractionService()

    root = tk.Tk()
    root.withdraw()

    path = filedialog.askopenfilename(
        title="Wybierz plik",
        filetypes=[
            ("Obrazy", "*.png *.jpg *.jpeg"),
            ("Pliki PNG", "*.png"),
            ("Pliki JPG", "*.jpg *.jpeg"),
            ("Wszystkie pliki", "*.*")
        ]
    )

    print(service.extract_data("vocab", "en", "B2", path))

if __name__ == "__main__":
    main()

