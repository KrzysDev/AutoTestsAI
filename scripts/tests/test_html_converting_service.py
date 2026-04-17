from backend.app.services.html_test_converter_service import HtmlConvertingService

service = HtmlConvertingService()

pdf = service.convert_html_to_pdf("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PDF Example</title>
    </head>
    <body>
        <h1>Hello, world!</h1>
    </body>
    </html>
""")

with open("output.pdf", "wb") as f:
    f.write(pdf)