import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from backend.app.services.json_test_converting_service import JsonTestConvertingService

def test_pdf_generation():
    test_json_path = os.path.join(root_dir, "test.json")
    output_pdf_path = os.path.join(root_dir, "generated_test.pdf")
    
    if not os.path.exists(test_json_path):
        raise FileNotFoundError(f"Nie znaleziono pliku: {test_json_path}")
        
    with open(test_json_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
        
    service = JsonTestConvertingService()
    service.convert_to_pdf(test_data, output_pdf_path)
    
    assert os.path.exists(output_pdf_path), "Błąd: Plik PDF nie został utworzony."
    assert os.path.getsize(output_pdf_path) > 0, "Błąd: Utworzony plik PDF jest pusty."
    
    print(f"Sukces! Plik PDF został wygenerowany poprawnie w: {output_pdf_path}")

if __name__ == "__main__":
    test_pdf_generation()
