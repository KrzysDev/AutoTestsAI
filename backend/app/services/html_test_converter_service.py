from xhtml2pdf import pisa
import io

class HtmlConvertingService:
    def convert_html_to_pdf(self, html_string):
        pdf_buffer = io.BytesIO()

        pisa_status = pisa.CreatePDF(
            html_string,
            dest=pdf_buffer
        )

        if pisa_status.err:
            return None

        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()

        return pdf_bytes