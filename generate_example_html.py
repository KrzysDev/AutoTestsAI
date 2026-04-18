import sys
import os

# Dodanie ścieżki do głównego katalogu projektu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.models.schemas import Form, FormSection
from backend.app.services.test_generator_service import TestGeneratorService

def main():
    service = TestGeneratorService()
    
    # Tworzenie przykładowego formularza (survey)
    example_form = Form(
        age_group="teens",
        level="B1",
        sections=[
            FormSection(
                task_type="grammar",
                subject="Present Simple",
                amount=1,
                additional_comment="Proste pytania wielokrotnego wyboru, typowe codzienne sytuacje nastolatków."
            ),
            FormSection(
                task_type="vocabulary",
                subject="School and Education",
                amount=1,
                additional_comment="Słownictwo związane ze szkołą, przedmiotami i nauką. Fill in the gaps."
            )
        ]
    )
    
    print("Rozpoczęto generowanie testu HTML na podstawie przykładu...")
    html_response = service.generate_html_test_from_survey(example_form)
    
    output_filename = "example_test.html"
    
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(html_response.response)
        
    print(f"Test został wygenerowany pomyślnie i zapisany jako {output_filename}")

if __name__ == "__main__":
    main()
