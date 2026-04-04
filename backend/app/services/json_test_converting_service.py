import os
from fpdf import FPDF
from app.models.schemas import Test

class JsonTestConvertingService:
    def convert_to_pdf(self, test_data: Test | dict) -> bytearray:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        if os.path.exists(font_path):
            pdf.add_font("Arial", "", font_path)
            font_family = "Arial"
        else:
            font_family = "Helvetica"

        groups = []
        if isinstance(test_data, dict):
            groups = test_data.get("groups", [])
        elif hasattr(test_data, "groups"):
            groups = test_data.groups

        for group_idx, group in enumerate(groups, start=1):
            pdf.add_page()
            pdf.set_font(font_family, size=12)

            header = "name:______________ surname:__________________ class:________________ date:____________________"
            pdf.multi_cell(0, 10, header)
            pdf.ln(10)

            if isinstance(group, dict):
                questions = group.get("questions", [])
                answers = group.get("answers", [])
            else:
                questions = getattr(group, "questions", [])
                answers = getattr(group, "answers", [])

            for i, question in enumerate(questions, start=1):
                if isinstance(question, dict):
                    q_text = question.get("text", "")
                    q_instruction = question.get("instruction", "")
                else:
                    q_text = getattr(question, "text", "")
                    q_instruction = getattr(question, "instruction", "")

                if q_instruction:
                    pdf.multi_cell(0, 10, f"Ex{i}. {q_instruction}\n{q_text}")
                else:
                    pdf.multi_cell(0, 10, f"Ex{i}:\n{q_text}")
                
                pdf.ln(5)

            pdf.add_page()
            pdf.set_font(font_family, size=14)
            pdf.multi_cell(0, 10, f"Klucz odpowiedzi (Grupa {group_idx})")
            pdf.ln(5)

            pdf.set_font(font_family, size=12)
            for i, answer in enumerate(answers, start=1):
                pdf.multi_cell(0, 10, f"Ex{i}:\n{answer}")
                pdf.ln(5)

        return pdf.output()
