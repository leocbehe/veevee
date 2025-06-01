import streamlit as st
from .config import settings
import os
import uuid
import numpy as np
from .models import DocumentChunk, KnowledgeBaseDocument
from pypdf import PdfReader

def read_tmp_document(file_name: str):
    abs_file_path = os.path.join(settings.app_dir, "tmp", file_name)
    print(f"Reading cache file {abs_file_path}")
    if file_name.endswith(".pdf"):
        return get_pdf_text(abs_file_path)
    else:
        with open(abs_file_path, "r", encoding="utf-8") as f:
            return f.read()

def get_embedded_chunks(document_text, document_id) -> list[dict]:
    from sentence_transformers import SentenceTransformer    
    model = SentenceTransformer('all-mpnet-base-v2')

    print("chunking text...")
    prog = st.progress(0, "(1 / 2) chunking text...")
    chunks = chunk_text(document_text, chunking_progress=prog)

    print("embedding chunks...")
    embedded_chunks = []
    n = len(chunks)
    prog.progress(0, "(2 / 2) embedding chunks...")
    for i, c in enumerate(chunks):
        prog.progress(float(i/n), "(2 / 2) embedding chunks...")
        emb = text_to_embedding(c, model)
        embedded_chunks.append({
            "document_id": document_id,
            "chunk_id": str(uuid.uuid4()),
            "chunk_text": c,
            "chunk_embedding": emb.tolist(),
        })
    return embedded_chunks

def get_document_text(doc):
    return read_tmp_document(doc['file_name'])

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

def delete_cache():
    cache_dir = os.path.join(settings.app_dir, "tmp")
    for file_name in os.listdir(cache_dir):
        os.remove(os.path.join(cache_dir, file_name))

def chunk_text(text: str, chunk_size: int = 1000, chunking_progress=None):
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except Exception:
        nltk.download('punkt')
        nltk.download('punkt_tab')
    from nltk.tokenize import sent_tokenize
    
    sentences = sent_tokenize(text)
    n = len(sentences)
    chunks = []
    current_chunk = ""
    previous_sentence = ""

    for i, sentence in enumerate(sentences):
        chunking_progress.progress(float(i/n), "(1 / 2) chunking text...")
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                print(f"appending chunk: {current_chunk}")
                chunks.append(current_chunk.strip())
            current_chunk = previous_sentence + " " + sentence + " "
        previous_sentence = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def text_to_embedding(chunk: str, model = None):
    if not model:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-mpnet-base-v2')
    embedding = np.array(model.encode(chunk))
    return embedding