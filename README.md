# pdf-generator

Instructions:

a) pip install dash pandas plotly pdfkit base64 dash-table kaleido

b) install wkhtmltopdf from https://wkhtmltopdf.org/

Changes to code:
1) Download google sheet in csv format and paste path on line 10 of the code

        file_path = "file-path-to-csv-file"  # Change to actual file path

2) on line 305

            try:
                config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
                pdfkit.from_string(html_content, pdf_path, configuration=config)
            except OSError:
                pdfkit.from_string(html_content, pdf_path)

change path to wkhtmltopdf.exe

and you are good to go

run python base.py on cmd after going to the directory and server should open on http://127.0.0.1:8050/

download files one by one
