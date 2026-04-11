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


class JsonTestConvertingService:

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Definiuje niestandardowe style akapitowe."""
        self.styles.add(ParagraphStyle(
            name="Header",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            name="ExerciseTitle",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            spaceBefore=10,
            spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            name="ExerciseInstruction",
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=13,
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            name="TestBodyText",
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            spaceAfter=4,
        ))
        self.styles.add(ParagraphStyle(
            name="CellText",
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name="CellBold",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
        ))

    def convert_to_pdf(self, test_data: PDFTest) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        story = []

        story.extend(self._build_student_header())
        story.append(Spacer(1, 0.5 * cm))

        for i, exercise in enumerate(test_data.exercises, start=1):
            story.extend(self._build_exercise(i, exercise))

        doc.build(story)
        buffer.seek(0)
        return buffer.read()

    # ------------------------------------------------------------------
    # Nagłówek
    # ------------------------------------------------------------------

    def _build_student_header(self) -> list:
        header_text = (
            "Name: ________________________  "
            "Class: ___________  "
            "Data: ___________"
        )
        return [Paragraph(header_text, self.styles["Header"])]

    # ------------------------------------------------------------------
    # Dispatcher ćwiczeń
    # ------------------------------------------------------------------

    def _build_exercise(self, index: int, exercise) -> list:
        fmt = exercise.formatting_type

        title = Paragraph(f"Zadanie {index}.", self.styles["ExerciseTitle"])
        instruction = Paragraph(exercise.instruction, self.styles["ExerciseInstruction"])

        dispatch = {
            "True-False":                  self._format_true_false,
            "Listening-Multiple-Choice":   self._format_multiple_choice,
            "Listeninig-Match-Inf":        self._format_match_information,
            "Listening-Insert":            self._format_insert,
            "Reading-Multiple-Choice":     self._format_multiple_choice,
            "Reading-Match-Headings":      self._format_match_headings,
        }

        formatter = dispatch.get(fmt, self._format_generic)
        body_elements = formatter(exercise.body)

        return [KeepTogether([title, instruction] + body_elements)]

    # ------------------------------------------------------------------
    # Formattery szczegółowe
    # ------------------------------------------------------------------

    def _format_true_false(self, body: str) -> list:
        sentences = [line.strip() for line in body.strip().splitlines() if line.strip()]

        col_widths = [10 * cm, 3 * cm, 3 * cm]

        header_row = [
            Paragraph("<b>Zdanie</b>", self.styles["CellBold"]),
            Paragraph("<b>True</b>", self.styles["CellBold"]),
            Paragraph("<b>False</b>", self.styles["CellBold"]),
        ]

        data = [header_row]
        for sentence in sentences:
            data.append([
                Paragraph(sentence, self.styles["TestBodyText"]),
                Paragraph("", self.styles["CellText"]),
                Paragraph("", self.styles["CellText"]),
            ])

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            # Nagłówek
            ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#4A90D9")),
            ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
            ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
            # Siatka
            ("GRID",         (0, 0), (-1, -1), 0.5, colors.grey),
            # Naprzemienne kolory wierszy
            *[("BACKGROUND", (0, i), (-1, i), colors.HexColor("#EAF2FB"))
              for i in range(2, len(data), 2)],
            # Wyrównanie zdania do lewej
            ("ALIGN",        (0, 1), (0, -1), "LEFT"),
            # Padding
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",   (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
            # Puste komórki True/False – widoczne okienka
            ("ROWBACKGROUND",(1, 1), (2, -1), colors.white),
        ]))

        return [Spacer(1, 0.2 * cm), table, Spacer(1, 0.4 * cm)]

    def _format_multiple_choice(self, body: str) -> list:
        """
        Formatuje zadanie wielokrotnego wyboru.
        Oczekiwany format body:
            Treść pytania
            A) opcja
            B) opcja
            C) opcja
            D) opcja
        Każde pytanie oddzielone pustą linią.
        """
        elements = []
        questions = body.strip().split("\n\n")

        col_widths = [1 * cm, 15 * cm]

        for q_block in questions:
            lines = [l.strip() for l in q_block.strip().splitlines() if l.strip()]
            if not lines:
                continue

            question_text = lines[0]
            options = lines[1:]

            elements.append(Paragraph(question_text, self.styles["TestBodyText"]))

            option_data = []
            for opt in options:
                # Rozdziel etykietę (A., A), 1.) od treści
                if len(opt) > 1 and opt[1] in (".", ")"):
                    label = opt[:2]
                    text = opt[2:].strip()
                else:
                    label = "•"
                    text = opt
                option_data.append([
                    Paragraph(label, self.styles["TestBodyText"]),
                    Paragraph(text, self.styles["TestBodyText"]),
                ])

            if option_data:
                opt_table = Table(option_data, colWidths=col_widths)
                opt_table.setStyle(TableStyle([
                    ("VALIGN",      (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING",  (0, 0), (-1, -1), 2),
                ]))
                elements.append(opt_table)

            elements.append(Spacer(1, 0.3 * cm))

        return elements

    def _format_match_information(self, body: str) -> list:
        """
        Match Information (Listening):
        Tworzy dwie kolumny – lewa z numerami/zdaniami, prawa z opcjami do dopasowania.
        Format body:
            1. Zdanie pierwsze
            2. Zdanie drugie
            ---
            A. Opcja A
            B. Opcja B
        Separator '---' dzieli zdania od opcji.
        """
        parts = body.strip().split("---")
        statements_raw = parts[0].strip().splitlines() if len(parts) > 0 else []
        options_raw = parts[1].strip().splitlines() if len(parts) > 1 else []

        statements = [l.strip() for l in statements_raw if l.strip()]
        options = [l.strip() for l in options_raw if l.strip()]

        max_rows = max(len(statements), len(options))
        data = []
        for i in range(max_rows):
            left = Paragraph(statements[i] if i < len(statements) else "", self.styles["TestBodyText"])
            right = Paragraph(options[i] if i < len(options) else "", self.styles["TestBodyText"])
            data.append([left, right])

        if not data:
            return [Paragraph(body, self.styles["TestBodyText"])]

        table = Table(data, colWidths=[8 * cm, 8 * cm])
        table.setStyle(TableStyle([
            ("GRID",         (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
            ("TOPPADDING",   (0, 0), (-1, -1), 4),
            ("BACKGROUND",   (1, 0), (1, -1), colors.HexColor("#F5F5F5")),
        ]))

        return [Spacer(1, 0.2 * cm), table, Spacer(1, 0.4 * cm)]

    def _format_insert(self, body: str) -> list:
        """
        Listening-Insert: tekst z lukami do uzupełnienia.
        Luki oznaczone jako ________ pozostają jak są,
        tekst renderowany jest z podkreśleniami widocznymi dla ucznia.
        """
        elements = []
        paragraphs = body.strip().split("\n\n")
        for para in paragraphs:
            if para.strip():
                elements.append(Paragraph(para.strip(), self.styles["TestBodyText"]))
                elements.append(Spacer(1, 0.15 * cm))
        return elements

    def _format_match_headings(self, body: str) -> list:
        """
        Reading-Match-Headings:
        Format body:
            Sekcja: treść akapitu
            ---
            A. Nagłówek A
            B. Nagłówek B
        Tworzy tabelę z numerem sekcji i polem na wpisanie nagłówka.
        """
        parts = body.strip().split("---")
        sections_raw = parts[0].strip().splitlines() if len(parts) > 0 else []
        headings_raw = parts[1].strip().splitlines() if len(parts) > 1 else []

        sections = [l.strip() for l in sections_raw if l.strip()]
        headings = [l.strip() for l in headings_raw if l.strip()]

        elements = []

        # Tabela: sekcje + pole odpowiedzi
        if sections:
            data = [[
                Paragraph("<b>Sekcja</b>", self.styles["CellBold"]),
                Paragraph("<b>Treść (fragment)</b>", self.styles["CellBold"]),
                Paragraph("<b>Nagłówek (wpisz literę)</b>", self.styles["CellBold"]),
            ]]
            for idx, sec in enumerate(sections, start=1):
                data.append([
                    Paragraph(str(idx), self.styles["CellText"]),
                    Paragraph(sec, self.styles["TestBodyText"]),
                    Paragraph("", self.styles["CellText"]),
                ])

            table = Table(data, colWidths=[1.5 * cm, 11 * cm, 3.5 * cm])
            table.setStyle(TableStyle([
                ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#4A90D9")),
                ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
                ("GRID",         (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN",        (0, 0), (0, -1), "CENTER"),
                ("ALIGN",        (2, 0), (2, -1), "CENTER"),
                ("LEFTPADDING",  (0, 0), (-1, -1), 6),
                ("TOPPADDING",   (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
                *[("BACKGROUND", (0, i), (-1, i), colors.HexColor("#EAF2FB"))
                  for i in range(2, len(data), 2)],
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.3 * cm))

        # Lista dostępnych nagłówków pod tabelą
        if headings:
            elements.append(Paragraph("<b>Dostępne nagłówki:</b>", self.styles["TestBodyText"]))
            for h in headings:
                elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{h}", self.styles["TestBodyText"]))
            elements.append(Spacer(1, 0.3 * cm))

        return elements

    def _format_generic(self, body: str) -> list:
        """Fallback – zwykły tekst."""
        elements = []
        for line in body.strip().splitlines():
            if line.strip():
                elements.append(Paragraph(line.strip(), self.styles["TestBodyText"]))
        elements.append(Spacer(1, 0.3 * cm))
        return elements