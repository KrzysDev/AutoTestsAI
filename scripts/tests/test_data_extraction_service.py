from backend.app.services.data_extraction_service import DataExtractionService

import tkinter as tk
from tkinter import filedialog

def main():
    service = DataExtractionService()

    root = tk.Tk()
    root.withdraw()

    path = filedialog.askopenfilename(
        title="Select file",
        filetypes=[
            ("Images", "*.png *.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("JPG files", "*.jpg *.jpeg"),
            ("All files", "*.*")
        ]
    )
    
    print("extracting data.....")
    print(service.extract_data(path, "vocab", "en", "B2"))

if __name__ == "__main__":
    main()

