from weasyprint import HTML

class HtmlConvertingService:
    def convert_html_to_pdf(self, html_string):
        try:
            pdf_bytes = HTML(string=html_string).write_pdf()
            return pdf_bytes
        except Exception:
            return None