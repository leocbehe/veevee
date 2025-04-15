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
    description: str
    model_path: str

class Chatbot(ChatbotBase):
    chatbot_id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    is_active: bool

class ChatbotCreate(ChatbotBase):
    owner_id: uuid.UUID
    configuration: Optional[dict] = None

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

"""Message schemas"""

class MessageBase(BaseModel):
    message_text: str
    role: str

class MessageCreate(MessageBase):
    message_id: Optional[uuid.UUID] = None
    conversation_id: uuid.UUID
    timestamp: datetime

class Message(MessageBase):
    conversation_id: uuid.UUID
    message_id: uuid.UUID
    timestamp: datetime

    class Config:
        from_attributes = True

"""Conversation schemas"""

class ConversationBase(BaseModel):
    conversation_id: uuid.UUID

class Conversation(ConversationBase):
    chatbot_id: uuid.UUID
    user_id: uuid.UUID
    description: Optional[str] = None
    start_time: datetime
    last_modified: Optional[datetime] = None
    messages: List[Message] = []

    class Config:
        from_attributes = True

class ConversationCreate(ConversationBase):
    user_id: uuid.UUID
    chatbot_id: uuid.UUID
    description: Optional[str] = None
    start_time: datetime
    last_modified: Optional[datetime] = None

class ConversationUpdate(ConversationBase):
    description: Optional[str] = None
    last_modified: Optional[datetime] = None
    is_active: Optional[bool] = None
    messages: Optional[List[MessageCreate]] = None

class ConversationDeletionConfirmation(ConversationBase):
    pass

"""JWT and auth schemas"""

class TokenData(BaseModel):
    user_id: str
    username: str
    issued_at: int

class Token(BaseModel):
    access_token: str
    token_type: str