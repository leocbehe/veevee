from .config import settings
import os
import io
from pypdf import PdfReader

def get_pdf_text(file_path: str):
    text = ""
    try:
        with open(file_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text().strip() + "\n\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def read_tmp_document(file_name: str):
    abs_file_path = os.path.join(settings.app_dir, "tmp", file_name)
    print(f"Reading cache file {abs_file_path}")
    if file_name.endswith(".pdf"):
        return get_pdf_text(abs_file_path)
    elif file_name.endswith(".txt"):
        with open(abs_file_path, "r") as f:
            return f.read()
