"""
Document Storage Models
Handles persistent storage of uploaded PDFs with PGVector embeddings
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

# Import PGVector
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    print("⚠️  PGVector not available for document storage")

from models.database import Base


class UserDocument(Base):
    """User uploaded document (PDF, etc.)"""
    __tablename__ = "user_documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey('conversations.id', ondelete='CASCADE'), index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # File info
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Processing info
    total_pages = Column(Integer)
    total_chunks = Column(Integer)
    
    # Privacy
    is_public = Column(Boolean, default=False, index=True)
    
    # Metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    doc_metadata = Column(JSON)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    conversation = relationship("Conversation", back_populates="documents")
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_size": self.file_size,
            "total_pages": self.total_pages,
            "total_chunks": self.total_chunks,
            "is_public": self.is_public,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None
        }


class DocumentChunk(Base):
    """Text chunk from document with embedding for vector search"""
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey('user_documents.id', ondelete='CASCADE'), index=True)
    user_id = Column(String, nullable=False, index=True)
    conversation_id = Column(String, ForeignKey('conversations.id', ondelete='CASCADE'), index=True)
    
    # Content
    chunk_text = Column(Text, nullable=False)
    
    # Vector embedding (384 dimensions for Sentence Transformers all-MiniLM-L6-v2)
    if PGVECTOR_AVAILABLE:
        chunk_embedding = Column(Vector(384))
    else:
        chunk_embedding = Column(JSON)  # Fallback to JSON if PGVector unavailable
    
    # Position info
    page_number = Column(Integer)
    chunk_index = Column(Integer)
    
    # Privacy (cached from parent document for faster queries)
    is_public = Column(Boolean, default=False, index=True)
    
    # Metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    doc_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("UserDocument", back_populates="chunks")


class UserStorageUsage(Base):
    """Track user storage quota"""
    __tablename__ = "user_storage_usage"
    
    user_id = Column(String, primary_key=True)
    total_storage_bytes = Column(Integer, default=0)
    document_count = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    @property
    def storage_mb(self):
        """Get storage in MB"""
        return self.total_storage_bytes / (1024 * 1024)
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "total_storage_mb": round(self.storage_mb, 2),
            "document_count": self.document_count,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
