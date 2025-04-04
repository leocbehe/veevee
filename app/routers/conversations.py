from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, database, models
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Conversation)
def create_conversation(conversation: schemas.ConversationCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Create a new conversation.
    """
    print(f"Creating conversation for user {current_user.user_id}")
    print(f"conversation: {conversation.model_dump()}")
    db_conversation = models.Conversation(**conversation.model_dump())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


@router.get("/{conversation_id}", response_model=schemas.Conversation)
def read_conversation(conversation_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve a conversation by its ID.
    """
    conversation = db.query(models.Conversation).filter(models.Conversation.conversation_id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("/", response_model=List[schemas.Conversation])
def read_conversations(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieve a list of conversations.
    """
    conversations = db.query(models.Conversation).filter(models.Conversation.user_id == current_user.user_id).offset(skip).limit(limit).all()
    return conversations


@router.put("/{conversation_id}", response_model=schemas.Conversation)
def update_conversation(conversation_id: str, conversation: schemas.ConversationUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Update a conversation.
    """
    db_conversation = db.query(models.Conversation).filter(models.Conversation.conversation_id == conversation_id).first()
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    for key, value in conversation.model_dump(exclude_unset=True).items():
        setattr(db_conversation, key, value)

    db.commit()
    db.refresh(db_conversation)
    return db_conversation


@router.delete("/{conversation_id}", response_model=schemas.Conversation)
def delete_conversation(conversation_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Delete a conversation.
    """
    conversation = db.query(models.Conversation).filter(models.Conversation.conversation_id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
    return conversation
