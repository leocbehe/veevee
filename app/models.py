from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, MetaData
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()
metadata = Base.metadata

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)
    password = Column(String)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    chatbots = relationship("Chatbot", back_populates="owner")
    conversations = relationship("Conversation", back_populates="user")


class Chatbot(Base):
    __tablename__ = "chatbots"

    chatbot_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    model_path = Column(String, nullable=True) # Can be a local path or a huggingface model name
    chatbot_name = Column(String)
    description = Column(String, nullable=True)
    modelfile = Column(String, nullable=True)
    configuration = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    owner = relationship("User", back_populates="chatbots")
    documents = relationship("KnowledgeBaseDocument", back_populates="chatbot")
    conversations = relationship("Conversation", back_populates="chatbot")


class KnowledgeBaseDocument(Base):
    __tablename__ = "knowledgebasedocuments"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chatbots.chatbot_id"))
    file_name = Column(String)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    document_metadata = Column(JSONB, nullable=True)
    context = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)
    embedding = Column(Vector(1536), nullable=True)  # Assuming your embeddings are 1536 dimensions, adjust if needed.
    chunks = relationship("DocumentChunk", back_populates="document")
    chatbot = relationship("Chatbot", back_populates="documents")


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chatbots.chatbot_id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    description = Column(String, nullable=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    last_modified = Column(DateTime(timezone=True), nullable=True)
    chatbot = relationship("Chatbot", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.conversation_id"))
    message_text = Column(Text)
    role = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    conversation = relationship("Conversation", back_populates="messages")

class DocumentChunk(Base):
    __tablename__ = "documentchunk"

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("knowledgebasedocuments.document_id"))
    chunk_text = Column(String)
    chunk_metadata = Column(JSONB, nullable=True)
    document = relationship("KnowledgeBaseDocument", back_populates="chunks")