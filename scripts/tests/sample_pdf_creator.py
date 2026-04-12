from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_full_exam_pdf(filename):
    # Ustawienia dokumentu
    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50)
    styles = getSampleStyleSheet()
    elements = []

    # Definicje stylów
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=1, spaceAfter=20)
    q_style = ParagraphStyle('Question', parent=styles['Normal'], spaceAfter=10, fontName='Helvetica-Bold', fontSize=11)
    text_style = ParagraphStyle('Text', parent=styles['Normal'], leading=14)
    
    elements.append(Paragraph("MOCK ENGLISH EXAM - COMPONENT REPOSITORY", title_style))

    # --- 1. MULTIPLE CHOICE (ASCII #1) ---
    elements.append(Paragraph("Task 1. Multiple Choice (A/B/C)", q_style))
    data = [
        ["1.", "What is the speaker's main intention?", ""],
        ["", "  ", "To complain about the broken laptop."],
        ["", "  ", "To ask for technical assistance."],
        ["", "  ", "To recommend a new store."]
    ]
    t1 = Table(data, colWidths=[20, 40, 380])
    t1.setStyle(TableStyle([
        ('GRID', (1, 1), (1, 3), 0.5, colors.black),
        ('ALIGN', (1, 1), (1, 3), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 20))

    # --- 2. MATCHING COLUMNS (ASCII #2) ---
    elements.append(Paragraph("Task 2. Match people with their opinions.", q_style))
    matching_data = [
        ["PEOPLE", "ANSWERS", "OPINIONS"],
        ["1. Mark Evans", "   ", "A. Believes tech is overrated."],
        ["2. Susan Bones", "   ", "B. Wants to move to Mars."],
        ["3. Tom Riddle", "   ", "C. Enjoys old-school libraries."]
    ]
    t2 = Table(matching_data, colWidths=[120, 70, 250])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 20))

    # --- 3. TRUE/FALSE/NOT GIVEN (ASCII #3) ---
    elements.append(Paragraph("Task 3. True / False", q_style))
    t3_data = [
        ["STATEMENTS", "T", "F"],
        ["1. The festival takes place every year.", "  ", "  "],
        ["2. Tickets are cheaper for students.", "  ", "  "],
        ["3. The main stage is near the lake.", "  ", "  "]
    ]
    t3 = Table(t3_data, colWidths=[330, 30, 30, 30])
    t3.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(t3)
    elements.append(Spacer(1, 20))

    # --- 4. WORD FORMATION SIDEBAR (ASCII #4) ---
    elements.append(Paragraph("Task 4. Word Formation Sidebar.", q_style))
    t4_data = [
        [Paragraph("The Internet has ___________________ (1) our communication.", text_style), "1. REVOLUTION"],
        [Paragraph("It is ________________ (2) to imagine life without it.", text_style), "2. POSSIBLE"]
    ]
    t4 = Table(t4_data, colWidths=[350, 100])
    t4.setStyle(TableStyle([
        ('LINEBEFORE', (1, 0), (1, -1), 1.5, colors.black),
        ('LEFTPADDING', (1, 0), (1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(t4)
    elements.append(Spacer(1, 20))

    # --- 5. TEXT-INSERTION BOX (ASCII #5) ---
    elements.append(Paragraph("Task 5. Insert the correct sentences into the gaps.", q_style))
    elements.append(Paragraph("I went to the store. [ 1 ]. However, it was closed. The sign said they would open at 10 AM. [ 2 ].", text_style))
    elements.append(Spacer(1, 10))
    
    sentences_data = [[Paragraph("A. It was a very sunny day.<br/>B. I decided to wait in a nearby cafe.<br/>C. I wanted to buy some fresh bread.", styles['Italic'])]]
    t5 = Table(sentences_data, colWidths=440)
    t5.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(t5)
    elements.append(Spacer(1, 20))

    # --- 6. TRANSFORMATIONS (ASCII #7) ---
    elements.append(Paragraph("Task 6. Key-Word Transformations.", q_style))
    t6_data = [
        ["1.", "I haven't seen him for two years."],
        ["", "LAST"],
        ["", "It _________________________________________ two years ago."]
    ]
    t6 = Table(t6_data, colWidths=[20, 420])
    t6.setStyle(TableStyle([
        ('BOX', (1, 1), (1, 1), 1, colors.black), # Ramka dla słowa LAST
        ('ALIGN', (1, 1), (1, 1), 'CENTER'),
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t6)
    elements.append(Spacer(1, 20))

    # --- 7. WRITING DRAFT AREA (ASCII #8) ---
    elements.append(Paragraph("Task 7. Writing Section.", q_style))
    # Ramka polecenia
    writing_prompt = [[Paragraph("Write an email to a friend about a recent trip. Describe the place and invite them.", styles['Normal'])]]
    t7 = Table(writing_prompt, colWidths=440)
    t7.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.black), ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 10), ('LEFTPADDING', (0,0), (-1,-1), 10)]))
    elements.append(t7)
    
    # Linie czystopisu
    elements.append(Spacer(1, 10))
    for _ in range(5):
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))

    doc.build(elements)

generate_full_exam_pdf("full_exam_layout.pdf")