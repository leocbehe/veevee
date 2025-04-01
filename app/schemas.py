from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

"""User schemas"""

class UserBase(BaseModel):
    username: str
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserModify(UserBase):
    username: Optional[str] = None
    email: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    password: Optional[str] = None
    created_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class User(UserBase):
    user_id: uuid.UUID
    is_active: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

"""Chatbot schemas"""

class ChatbotBase(BaseModel):
    chatbot_name: str
    description: Optional[str] = None
    modelfile: Optional[str] = None
    configuration: Optional[dict] = None
    model_path: Optional[str] = None

class Chatbot(ChatbotBase):
    chatbot_id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class ChatbotUpdate(Chatbot):
    pass

"""RAG document schemas"""

class KnowledgeBaseDocumentBase(BaseModel):
    file_name: str
    metadata: Optional[dict] = None

class KnowledgeBaseDocumentCreate(KnowledgeBaseDocumentBase):
    pass

class KnowledgeBaseDocument(KnowledgeBaseDocumentBase):
    document_id: uuid.UUID
    chatbot_id: uuid.UUID
    file_path: str
    upload_date: datetime

    class Config:
        from_attributes = True

"""Conversation schemas"""

class ConversationBase(BaseModel):
    pass

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    conversation_id: uuid.UUID
    chatbot_id: uuid.UUID
    user_id: uuid.UUID
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True

"""Message schemas"""

class MessageBase(BaseModel):
    message_text: str
    is_user_message: bool
    retrieved_context: Optional[dict] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    message_id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: Optional[uuid.UUID] = None
    timestamp: datetime

    class Config:
        from_attributes = True

"""JWT and auth schemas"""

class JWTPayload(BaseModel):
    user_id: str
    username: str
    issued_at: int

class Token(BaseModel):
    access_token: str
    token_type: str