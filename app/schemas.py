from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

"""User schemas"""

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
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
    chatbot_id: uuid.UUID
    chatbot_name: str
    description: str
    model_name: str

class Chatbot(ChatbotBase):
    owner_id: uuid.UUID
    created_at: datetime
    is_active: bool
    configuration: dict

class ChatbotCreate(ChatbotBase):
    owner_id: uuid.UUID
    created_at: datetime
    configuration: Optional[dict] = None

    class Config:
        from_attributes = True

class ChatbotUpdate(BaseModel):
    chatbot_name: Optional[str] = None
    description: Optional[str] = None
    model_name: Optional[str] = None
    configuration: Optional[dict] = None

"""RAG document schemas"""

class KnowledgeBaseDocumentBase(BaseModel):
    document_id: uuid.UUID
    chatbot_id: uuid.UUID
    file_name: str

class KnowledgeBaseDocument(KnowledgeBaseDocumentBase):
    created_at: datetime
    file_path: Optional[str]
    context: Optional[str]
    document_metadata: Optional[dict] = None
    raw_text: Optional[str] = None

class KnowledgeBaseDocumentCreate(KnowledgeBaseDocumentBase):
    context: str
    created_at: datetime
    file_path: Optional[str] = None
    document_metadata: Optional[dict] = None
    raw_text: Optional[str] = None

class KnowledgeBaseDocumentUpdate(BaseModel):
    chatbot_id: Optional[uuid.UUID] = None
    file_name: Optional[str] = None
    context: Optional[str] = None
    file_path: Optional[str] = None
    document_metadata: Optional[dict] = None
    raw_text: Optional[str] = None

    class Config:
        from_attributes = True

"""Document chunk schemas"""

class DocumentChunkBase(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    chunk_metadata: Optional[dict] = None

class DocumentChunk(DocumentChunkBase):
    chunk_text: str
    chunk_embedding: List[float]

class DocumentChunkText(DocumentChunkBase):
    chunk_text: str

class DocumentChunkEmbedding(DocumentChunkBase):
    chunk_embedding: List[float]

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