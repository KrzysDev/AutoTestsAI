import os
import json
from fpdf import FPDF
from backend.app.models.schemas import GeneratedTest, Exercise

# <summary>
# Service for converting generated tests into output formats such as JSON and PDF.
# </summary>
class JsonTestConvertingService:
    def save_to_json(self, test_data: GeneratedTest, filepath: str = "generated_test.json"):
        data = test_data.model_dump()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def convert_to_pdf(self, test_data: GeneratedTest | dict) -> bytearray:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Arial", "", font_path)
            font_family = "Arial"
        else:
            font_family = "Helvetica"

        pdf.add_page()
        pdf.set_font(font_family, size=12)

        header = "name:______________ surname:__________________ class:________________ date:____________________"
        pdf.multi_cell(0, 10, header)
        pdf.ln(10)

        exercises = []
        if isinstance(test_data, dict):
            exercises = test_data.get("exercises", [])
        elif hasattr(test_data, "exercises"):
            exercises = test_data.exercises

        for i, exercise in enumerate(exercises, start=1):
            if isinstance(exercise, dict):
                instruction = exercise.get("instruction", "")
                body = exercise.get("body", "")
            else:
                instruction = getattr(exercise, "instruction", "")
                body = getattr(exercise, "body", "")
            
            pdf.multi_cell(0, 10, f"Ex{i}. {instruction}\n{body}")
            pdf.ln(5)
        
        return pdf.output()
