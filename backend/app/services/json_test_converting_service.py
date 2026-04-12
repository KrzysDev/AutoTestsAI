import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from backend.app.models.schemas import PDFTest, PDFExercise
from reportlab.lib.enums import TA_LEFT, TA_CENTER


import io
from typing import List, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from backend.app.models.schemas import (
    PDFTest, PDFExercise, MultipleChoiceExercise, MatchingExercise,
    TrueFalseExercise, WordFormationExercise, GapFillExercise,
    TransformationExercise, WritingExercise, ClozeExercise, SimpleTextExercise
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


class JsonTestConvertingService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.title_style = ParagraphStyle(
            'Title', 
            parent=self.styles['Heading1'], 
            alignment=TA_CENTER, 
            spaceAfter=20,
            fontSize=18,
            textColor=colors.HexColor("#2C3E50")
        )
        self.q_style = ParagraphStyle(
            'QuestionHeader', 
            parent=self.styles['Normal'], 
            spaceAfter=12, 
            fontName='Helvetica-Bold', 
            fontSize=12,
            textColor=colors.HexColor("#2980B9")
        )
        self.text_style = ParagraphStyle(
            'Text', 
            parent=self.styles['Normal'], 
            leading=16,
            fontSize=11
        )
        self.italic_style = ParagraphStyle(
            'ItalicText', 
            parent=self.styles['Normal'], 
            fontName='Helvetica-Oblique',
            fontSize=10,
            textColor=colors.grey
        )

    def convert_to_pdf(self, test_data: PDFTest) -> bytes:
        """
        Converts structured test data into a formatted PDF byte stream.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            leftMargin=50, 
            rightMargin=50, 
            topMargin=50, 
            bottomMargin=50
        )
        elements = []
        
        # Add Title
        elements.append(Paragraph("ENGLISH LANGUAGE TEST", self.title_style))
        elements.append(Paragraph("Name:___________________ Last Name:____________________"), self.text_style)
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#BDC3C7"), spaceAfter=20))
        
        # Process Exercises
        for i, exercise in enumerate(test_data.exercises, 1):
            exercise_elements = self._process_exercise(exercise, i)
            if exercise_elements:
                if len(exercise_elements) > 1:
                    # Keep instruction header and the first element of the task together
                    # to prevent "orphan" headers at the bottom of a page.
                    elements.append(KeepTogether(exercise_elements[:2]))
                    # Allow the rest of the task elements to flow and split across pages naturally.
                    elements.extend(exercise_elements[2:])
                else:
                    elements.extend(exercise_elements)
                
                elements.append(Spacer(1, 25))
            
        doc.build(elements)
        return buffer.getvalue()

    def _process_exercise(self, exercise: PDFExercise, index: int) -> List[Any]:
        """
        Dispatches exercise data to the appropriate drawing helper.
        """

        elements = []

        if exercise.instruction.lower() == "answer key":
            elements.append(Paragraph(f"Answer key (Dont print this): "), self.title_style)
            elements.append(Paragraph(f"{exercise.body}"), self.text_style)
            return elements

        # Add Instruction Header
        elements.append(Paragraph(f"Task {index}. {exercise.instruction}", self.q_style))
        
        if isinstance(exercise, MultipleChoiceExercise):
            elements.extend(self._draw_multiple_choice(exercise))
        elif isinstance(exercise, MatchingExercise):
            elements.extend(self._draw_matching(exercise))
        elif isinstance(exercise, TrueFalseExercise):
            elements.extend(self._draw_true_false(exercise))
        elif isinstance(exercise, WordFormationExercise):
            elements.extend(self._draw_word_formation(exercise))
        elif isinstance(exercise, GapFillExercise):
            elements.extend(self._draw_gap_fill(exercise))
        elif isinstance(exercise, TransformationExercise):
            elements.extend(self._draw_transformation(exercise))
        elif isinstance(exercise, WritingExercise):
            elements.extend(self._draw_writing(exercise))
        elif isinstance(exercise, ClozeExercise):
            elements.extend(self._draw_cloze(exercise))
        elif isinstance(exercise, SimpleTextExercise):
            elements.extend(self._draw_simple_text(exercise))
            
        return elements

    def _draw_multiple_choice(self, exercise: MultipleChoiceExercise) -> List[Any]:
        elements = []
        for i, q in enumerate(exercise.questions, 1):
            data = [[f"{i}.", q.question]]
            for j, opt in enumerate(q.options):
                data.append(["", f" {chr(ord('A') + j)} ", opt])
            
            t = Table(data, colWidths=[20, 40, 380])
            t.setStyle(TableStyle([
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 8))
        return elements

    def _draw_matching(self, exercise: MatchingExercise) -> List[Any]:
        header = [["ITEMS", "ANSWERS", "OPTIONS"]]
        data = []
        max_len = max(len(exercise.left_column), len(exercise.right_column))
        
        for i in range(max_len):
            left = exercise.left_column[i] if i < len(exercise.left_column) else ""
            right = exercise.right_column[i] if i < len(exercise.right_column) else ""
            data.append([left, f"  ", right])
            
        t = Table(header + data, colWidths=[140, 80, 220], repeatRows=1)
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (1, 1), (1, -1), 0.5, colors.grey),
        ]))
        return [t]

    def _draw_true_false(self, exercise: TrueFalseExercise) -> List[Any]:
        header = [["STATEMENTS", "T", "F"]]
        data = [[Paragraph(s, self.text_style), " ", " "] for s in exercise.statements]
        
        t = Table(header + data, colWidths=[360, 40, 40], repeatRows=1)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        return [t]

    def _draw_word_formation(self, exercise: WordFormationExercise) -> List[Any]:
        data = []
        for i, item in enumerate(exercise.items, 1):
            data.append([
                Paragraph(item.sentence_with_gap, self.text_style), 
                f"{i}. {item.root_word}"
            ])
            
        t = Table(data, colWidths=[340, 110])
        t.setStyle(TableStyle([
            ('LINEBEFORE', (1, 0), (1, -1), 1.5, colors.black),
            ('LEFTPADDING', (1, 0), (1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        return [t]

    def _draw_gap_fill(self, exercise: GapFillExercise) -> List[Any]:
        elements = []
        elements.append(Paragraph(exercise.passage, self.text_style))
        elements.append(Spacer(1, 15))
        
        choices_text = "<br/>".join(exercise.choices)
        choices_table_data = [[Paragraph(choices_text, self.italic_style)]]
        
        t = Table(choices_table_data, colWidths=440)
        t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t)
        return elements

    def _draw_transformation(self, exercise: TransformationExercise) -> List[Any]:
        elements = []
        for i, item in enumerate(exercise.items, 1):
            data = [
                [f"{i}.", item.original_sentence],
                ["", item.key_word],
                ["", item.sentence_with_gap]
                ["\n", ""]
            ]
            t = Table(data, colWidths=[20, 420])
            t.setStyle(TableStyle([
                ('BOX', (1, 1), (1, 1), 1, colors.black),
                ('ALIGN', (1, 1), (1, 1), 'CENTER'),
                ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 15))
        return elements

    def _draw_writing(self, exercise: WritingExercise) -> List[Any]:
        elements = []
        prompt_data = [[Paragraph(exercise.prompt, self.text_style)]]
        t = Table(prompt_data, colWidths=440)
        t.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F9FBFC"))
        ]))
        elements.append(t)
        
        if exercise.word_count_range:
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(f"[ Word count: ________ / {exercise.word_count_range} ]", self.italic_style))
            
        elements.append(Spacer(1, 15))
        for _ in range(8):
            elements.append(Spacer(1, 15))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
            
        return elements

    def _draw_cloze(self, exercise: ClozeExercise) -> List[Any]:
        elements = []
        elements.append(Paragraph(exercise.passage, self.text_style))
        elements.append(Spacer(1, 15))
        
        for opt_group in exercise.options_per_gap:
            opts_text = "   ".join(opt_group.options)
            elements.append(Paragraph(f"<b>{opt_group.gap_number}.</b> {opts_text}", self.text_style))
            elements.append(Spacer(1, 4))
            
        return elements

    def _draw_simple_text(self, exercise: SimpleTextExercise) -> List[Any]:
        return [Paragraph(exercise.body, self.text_style)]

    