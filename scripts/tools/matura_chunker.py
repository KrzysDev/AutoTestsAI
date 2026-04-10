import os
import json
import sys
import tkinter as tk
from tkinter import filedialog
from pypdf import PdfReader

# Add project root to sys.path to allow imports from backend
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.app.services.chunking_service import ChunkingService

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts all text from a PDF file using pypdf."""
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return text

def main():
    # Initialize tkinter for folder selection
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True) # Bring dialog to front
    
    # Prompt for folder selection
    print("Oczekiwanie na wybór folderu...")
    folder_path = filedialog.askdirectory(title="Wybierz folder zawierający arkusze PDF")
    
    if not folder_path:
        print("Nie wybrano żadnego folderu. Przerywam.")
        return

    # Find all PDF files in the directory
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"W folderze {folder_path} nie znaleziono żadnych plików PDF.")
        return

    print(f"Znaleziono {len(pdf_files)} plików PDF. Rozpoczynam przetwarzanie...")
    
    chunker = ChunkingService()
    results = {}

    for pdf_name in pdf_files:
        full_path = os.path.join(folder_path, pdf_name)
        print(f"Przetwarzanie: {pdf_name}...")
        
        # 1. Extract text
        raw_text = extract_text_from_pdf(full_path)
        
        # 2. Chunk text into tasks
        tasks = chunker.chunk_matura(raw_text)
        
        results[pdf_name] = {
            "task_count": len(tasks),
            "tasks": tasks
        }
        print(f"  - Znaleziono {len(tasks)} zadań.")

    # Save the chunked tasks to a JSON file
    output_dir = os.path.join(project_root, "data", "extracted_tasks")
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "matura_chunks.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\nSukces! Wyekstrahowane zadania zapisano w: {output_file}")

if __name__ == "__main__":
    main()
