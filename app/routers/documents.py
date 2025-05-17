from ..database import get_db

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..rag_utils import read_tmp_document, chunk_text, text_to_embedding
from typing import List

from app import models, schemas
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.KnowledgeBaseDocumentCreate, status_code=status.HTTP_201_CREATED)
def create_document(document: schemas.KnowledgeBaseDocumentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Create a new document.
    """
    # Verify that the chatbot exists and the current user owns it
    chatbot = db.query(models.Chatbot).filter(models.Chatbot.chatbot_id == document.chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    if chatbot.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add documents to this chatbot")

    db_document = models.KnowledgeBaseDocument(**document.model_dump())
    db_document.raw_text = read_tmp_document(document.file_name)
    chunks = chunk_text(db_document.raw_text)
    
    for c in chunks:
        emb = text_to_embedding(c)
        document_chunk = models.DocumentChunk(document_id=db_document.document_id, chunk_text=c, chunk_embedding=emb)
        db_document.chunks.append(document_chunk)

    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.get("/{document_id}", response_model=schemas.KnowledgeBaseDocument)
def read_document(document_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve a document by its ID.
    """
    db_document = db.query(models.KnowledgeBaseDocument).filter(models.KnowledgeBaseDocument.document_id == document_id).first()
    if db_document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Verify that the current user owns the chatbot associated with the document
    chatbot = db.query(models.Chatbot).filter(models.Chatbot.chatbot_id == db_document.chatbot_id).first()
    if chatbot.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this document")

    return db_document

@router.put("/{document_id}", response_model=schemas.KnowledgeBaseDocumentUpdate)
def update_document(document_id: str, document: schemas.KnowledgeBaseDocumentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Update a document.
    """
    db_document = db.query(models.KnowledgeBaseDocument).filter(models.KnowledgeBaseDocument.document_id == document_id).first()
    if db_document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Verify that the current user owns the chatbot associated with the document
    chatbot = db.query(models.Chatbot).filter(models.Chatbot.chatbot_id == db_document.chatbot_id).first()
    if chatbot.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this document")

    # Update the document with the new values
    for key, value in document.model_dump().items():
        setattr(db_document, key, value)

    db.commit()
    db.refresh(db_document)
    return db_document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Delete a document.
    """
    db_document = db.query(models.KnowledgeBaseDocument).filter(models.KnowledgeBaseDocument.document_id == document_id).first()
    if db_document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Verify that the current user owns the chatbot associated with the document
    chatbot = db.query(models.Chatbot).filter(models.Chatbot.chatbot_id == db_document.chatbot_id).first()
    if chatbot.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this document")

    db.delete(db_document)
    db.commit()
    return

@router.get("/by_chatbot/{chatbot_id}", response_model=List[schemas.KnowledgeBaseDocument])
def read_documents_by_chatbot(chatbot_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve all documents associated with a given chatbot ID.
    """
    # Verify that the chatbot exists and the current user owns it
    chatbot = db.query(models.Chatbot).filter(models.Chatbot.chatbot_id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found")
    if chatbot.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view documents for this chatbot")

    documents = db.query(models.KnowledgeBaseDocument).filter(models.KnowledgeBaseDocument.chatbot_id == chatbot_id).all()
    return documents

@router.post("/document_chunks", response_model=List[schemas.DocumentChunk])
def get_document_chunks(document_ids: List[str], db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve document chunks by document IDs.
    """
    print(f"Received document IDs: {document_ids}")

    chunks = db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id.in_(document_ids)).all()
    return chunks
