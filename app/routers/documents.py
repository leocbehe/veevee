from ..database import get_db

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..rag import read_tmp_document

from app import models, schemas, database
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

    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.get("/{document_id}", response_model=schemas.KnowledgeBaseDocumentCreate)
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

@router.put("/{document_id}", response_model=schemas.KnowledgeBaseDocumentCreate)
def update_document(document_id: str, document: schemas.KnowledgeBaseDocumentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
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