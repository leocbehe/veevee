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

@router.get("/by_chatbot/{chatbot_id}", response_model=List[schemas.Conversation])
def read_conversations_by_chatbot(chatbot_id: str, db: Session = Depends(database.get_db), skip: int = 0, limit: int = 10, current_user: models.User = Depends(get_current_user)):
    """
    Retrieve a list of conversations by chatbot ID.
    """
    chatbot = db.query(models.Chatbot).filter(models.Chatbot.chatbot_id == chatbot_id).first()
    if current_user.user_id != chatbot.owner_id:
        raise HTTPException(status_code=403, detail="Forbidden: You are not the owner of this chatbot")
    conversations = db.query(models.Conversation).filter(models.Conversation.chatbot_id == chatbot_id).offset(skip).limit(limit).all()
    return conversations


@router.put("/", response_model=schemas.Conversation)
def update_conversation(conversation: schemas.ConversationUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Update a conversation.
    """
    db_conversation = db.query(models.Conversation).filter(models.Conversation.conversation_id == conversation.conversation_id).first()
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation.messages:
        messages = [schemas.MessageCreate(**message.model_dump()) for message in conversation.messages]

    # Update the conversation object with all values except for messages
    for key, value in conversation.model_dump(exclude_unset=True, exclude={"messages"}).items():
        setattr(db_conversation, key, value)

    # update the Messages in the conversation by updating the Messages table in the database
    for message in messages:
        if message.message_id is None:
            db_message = models.Message(**message.model_dump())
            db.add(db_message)
        else:
            db_message = db.query(models.Message).filter(models.Message.message_id == message.message_id).first()
            if db_message is None:
                db_message = models.Message(**message.model_dump())
                db.add(db_message)

    db.commit()
    db.refresh(db_conversation)
    return db_conversation


@router.delete("/{conversation_id}", response_model=schemas.ConversationDeletionConfirmation)
def delete_conversation(conversation_id: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    Delete a conversation.
    """
    conversation = db.query(models.Conversation).filter(models.Conversation.conversation_id == conversation_id).first()
    deleted_conversation_id = conversation.conversation_id
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
    return schemas.ConversationDeletionConfirmation(conversation_id=conversation.conversation_id)
