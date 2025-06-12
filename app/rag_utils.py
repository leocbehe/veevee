import streamlit as st
from .config import settings
import os
import uuid
import numpy as np
from .models import DocumentChunk, KnowledgeBaseDocument
from pypdf import PdfReader
from streamlit.runtime.uploaded_file_manager import UploadedFile
import io

def get_embedded_chunks(document_text, document_id, chunk_metadata=None) -> list[dict]:
    
    chunks = chunk_text(document_text, chunk_size=settings.chunk_size)
    embedded_chunks = []
    n = len(chunks)
    for i, c in enumerate(chunks):
        emb = text_to_embedding(c)
        embedded_chunk = {
            "document_id": str(document_id),
            "chunk_id": str(uuid.uuid4()),
            "chunk_text": c,
            "chunk_embedding": emb.tolist(),
        }
        if chunk_metadata:
            embedded_chunk['chunk_metadata'] = chunk_metadata
        embedded_chunks.append(embedded_chunk)


    return embedded_chunks

def read_text_file(text_file: UploadedFile):
    """Reads the content of a text file and returns it as a string."""
    try:
        return text_file.read().decode(encoding='utf-8')
    except Exception as e:
        print(f"Error reading text file: {e}")
        return None

def read_pdf_file(pdf_file: UploadedFile):
    """Reads the content of a PDF file and returns it as a string."""
    try:
        # prog = st.progress(0, "reading pdf...")
        pdf_reader = PdfReader(pdf_file)
        text = ""
        n = len(pdf_reader.pages)
        for i, page in enumerate(pdf_reader.pages):
            # prog.progress(float(i/n), f"({i} / {n}) reading pdf...")
            text += page.extract_text().replace('\x00', '')
        return text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

def delete_cache():
    cache_dir = os.path.join(settings.app_dir, "tmp")
    for file_name in os.listdir(cache_dir):
        os.remove(os.path.join(cache_dir, file_name))

def chunk_text(text: str, chunk_size: int = settings.chunk_size, chunking_progress=None):
    # if not chunking_progress:
    #     chunking_progress = st.progress(0, "chunking text...")

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
        # chunking_progress.progress(float(i/n), f"({i}/{n}) chunking text...")
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

def text_to_embedding(chunk: str, model=None):
    if not model:
        try:
            import sentence_transformers
            model = sentence_transformers.SentenceTransformer('all-mpnet-base-v2')
        except Exception as e:
            print(f"Error loading Sentence Transformers: {e}")
            return None
    embedding = np.array(model.encode(chunk))
    return embedding