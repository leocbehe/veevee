import streamlit as st
from .config import settings
import os
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize
from pypdf import PdfReader
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

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
    else:
        with open(abs_file_path, "r", encoding="utf-8") as f:
            return f.read()

def delete_cache():
    cache_dir = os.path.join(settings.app_dir, "tmp")
    for file_name in os.listdir(cache_dir):
        os.remove(os.path.join(cache_dir, file_name))

def chunk_text(text: str, chunk_size: int = 1000):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    previous_sentence = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = previous_sentence + " " + sentence + " "
        previous_sentence = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

@st.cache_resource
def load_embedding_model():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-mpnet-base-v2')
    return model

def text_to_embedding(chunk: str):
    model = load_embedding_model()
    embedding = np.array(model.encode(chunk))
    return embedding