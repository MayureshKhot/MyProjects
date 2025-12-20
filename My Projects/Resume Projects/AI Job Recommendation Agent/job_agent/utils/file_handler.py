from PyPDF2 import PdfReader

def parse_resume(file_path):
    full_text=""
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            extracted = page.extract_text()
            # full_text += page.extract_text()
            if extracted:
                full_text += extracted
    return full_text