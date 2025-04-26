from .config import settings
import os

def read_tmp_document(file_name: str):
    print(f"Reading file {file_name} from {settings.app_dir}")
    abs_file_path = os.path.join(settings.app_dir, "tmp", file_name)
    if file_name.endswith(".pdf"):
        pass
        # return read_pdf_document(file_name)
    elif file_name.endswith(".txt"):
        with open(abs_file_path, "r") as f:
            return f.read()
