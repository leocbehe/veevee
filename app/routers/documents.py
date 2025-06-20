from ..database import get_db
from ..rag_utils import get_embedded_chunks, text_to_embedding

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.oauth2 import get_current_user

import uuid

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED)
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

    # convert the list of dictionaries from the document into a list of DocumentChunk objects
    chunk_objects = []
    if document.chunks:
        for chunk in document.chunks:
            chunk_objects.append(models.DocumentChunk(
                chunk_id=uuid.uuid4(),
                document_id=document.document_id,
                chunk_text=chunk.chunk_text,
                chunk_embedding=chunk.chunk_embedding,
            ))

    # create a sqlalchemy object with the same fields but using the DocumentChunk objects instead of the dictionaries
    db_document = models.KnowledgeBaseDocument(
        document_id=document.document_id,
        chatbot_id=document.chatbot_id,
        file_name=document.file_name,
        raw_text=document.raw_text,
        context=document.context,
        created_at=document.created_at,
        chunks=chunk_objects,
        )
    
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
        if value is not None:
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

    chunks = db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id.in_(document_ids)).all()
    return chunks

@router.post("/create_embedded_document_chunks", response_model=List[schemas.DocumentChunk])
def create_embedded_document_chunks(embedded_document_request: schemas.CreateEmbeddedDocumentChunks, db: Session = Depends(get_db)):
    """
    Create embedded document chunks from the provided text.
    """
    embedded_chunks = get_embedded_chunks(
        embedded_document_request.document_text,
        embedded_document_request.document_id,
        embedded_document_request.chunk_metadata,
    )

    # Convert the list of dictionaries to a list of DocumentChunk objects
    document_chunks = []
    for chunk in embedded_chunks:
        document_chunks.append(
            schemas.DocumentChunk(
                chunk_id=uuid.UUID(chunk["chunk_id"]),
                document_id=uuid.UUID(chunk["document_id"]),
                chunk_text=chunk["chunk_text"],
                chunk_embedding=chunk["chunk_embedding"],
                chunk_metadata=chunk.get("chunk_metadata"),
            )
        )
    return document_chunks

@router.post("/get_chunk_embedding", response_model=schemas.ChunkEmbedding)
def get_chunk_embedding(chunk_embedding_request: schemas.ChunkEmbedding):
    """
    Generate an embedding for the given text.
    """
    embedding = text_to_embedding(chunk_embedding_request.chunk_text)
    if embedding is not None:
        return schemas.ChunkEmbedding(chunk_text=chunk_embedding_request.chunk_text, chunk_embedding=embedding.tolist())
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate embedding")