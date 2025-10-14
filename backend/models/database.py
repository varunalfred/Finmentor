"""
Database Models for FinMentor AI
Using SQLAlchemy with PostgreSQL
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid

Base = declarative_base()

# ============= User Models =============

class User(Base):
    """User account model"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)

    # Profile information
    age = Column(Integer)
    user_type = Column(String(50), default="beginner")  # beginner, intermediate, advanced
    education_level = Column(String(50), default="basic")
    risk_tolerance = Column(String(50), default="moderate")  # low, moderate, high
    financial_goals = Column(JSON, default=list)  # List of goals
    preferred_language = Column(String(10), default="en")
    preferred_output = Column(String(20), default="text")  # text, voice, visual

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    learning_progress = relationship("LearningProgress", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "user_type": self.user_type,
            "education_level": self.education_level,
            "risk_tolerance": self.risk_tolerance,
            "financial_goals": self.financial_goals,
            "is_premium": self.is_premium,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# ============= Conversation Models =============

class Conversation(Base):
    """Conversation/chat session model"""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255))
    topic = Column(String(100))  # stocks, education, planning, etc.

    # Conversation metadata
    total_messages = Column(Integer, default=0)
    context = Column(JSON, default=dict)  # Conversation context/memory
    sentiment = Column(Float)  # Average sentiment score
    satisfaction_rating = Column(Integer)  # User rating 1-5

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_user_conversations', 'user_id', 'created_at'),
    )

class Message(Base):
    """Individual message in a conversation"""
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Message content
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    input_type = Column(String(20), default="text")  # text, voice, image, document

    # Vector embedding for semantic search (1536 dims for OpenAI, 768 for Gemini)
    embedding = Column(Vector(1536))

    # Multimodal data
    voice_data = Column(Text)  # Base64 encoded audio
    image_data = Column(Text)  # Base64 encoded image
    document_data = Column(Text)  # Base64 encoded document

    # Response data
    response_data = Column(JSON)  # Structured data from APIs
    visual_response = Column(JSON)  # Chart/graph data

    # Metadata
    confidence_score = Column(Float)
    processing_time = Column(Float)  # In seconds
    tokens_used = Column(Integer)
    model_used = Column(String(50))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User", back_populates="messages")
    feedback = relationship("MessageFeedback", back_populates="message", uselist=False)

    # Indexes
    __table_args__ = (
        Index('idx_conversation_messages', 'conversation_id', 'created_at'),
    )

class MessageFeedback(Base):
    """User feedback on message quality"""
    __tablename__ = "message_feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("messages.id"), unique=True, nullable=False)

    helpful = Column(Boolean)
    accurate = Column(Boolean)
    rating = Column(Integer)  # 1-5 stars
    feedback_text = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    message = relationship("Message", back_populates="feedback")

# ============= Financial Data Models =============

class Portfolio(Base):
    """User's investment portfolio"""
    __tablename__ = "portfolios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)

    # Portfolio details
    total_value = Column(Float, default=0.0)
    cash_balance = Column(Float, default=0.0)
    is_virtual = Column(Boolean, default=True)  # Practice portfolio

    # Performance metrics
    total_return = Column(Float)
    daily_return = Column(Float)
    risk_score = Column(Float)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")

class Holding(Base):
    """Individual holding in a portfolio"""
    __tablename__ = "holdings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)

    symbol = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_price = Column(Float)
    current_value = Column(Float)

    # Performance
    total_return = Column(Float)
    percentage_return = Column(Float)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")

class Transaction(Base):
    """Buy/sell transactions"""
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)

    type = Column(String(10), nullable=False)  # buy, sell
    symbol = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)

    # Additional info
    notes = Column(Text)

    # Timestamps
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")

    # Indexes
    __table_args__ = (
        Index('idx_portfolio_transactions', 'portfolio_id', 'executed_at'),
    )

# ============= Learning/Education Models =============

class LearningProgress(Base):
    """Track user's learning progress"""
    __tablename__ = "learning_progress"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Progress tracking
    current_level = Column(Integer, default=1)  # 1-4 (Beginner to Expert)
    xp_points = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)

    # Completed content
    completed_topics = Column(JSON, default=list)
    completed_lessons = Column(JSON, default=list)
    achievements = Column(JSON, default=list)

    # Quiz scores
    quiz_attempts = Column(Integer, default=0)
    average_score = Column(Float)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="learning_progress")

class EducationalContent(Base):
    """Educational content library"""
    __tablename__ = "educational_content"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    title = Column(String(255), nullable=False)
    topic = Column(String(100), nullable=False, index=True)
    level = Column(String(50), nullable=False)  # beginner, intermediate, advanced
    content_type = Column(String(50))  # article, video, quiz

    # Content
    content = Column(Text, nullable=False)
    summary = Column(Text)
    key_points = Column(JSON)

    # Vector embedding for semantic search
    embedding = Column(Vector(1536))

    # Metadata
    duration_minutes = Column(Integer)
    difficulty_score = Column(Integer)  # 1-10

    # Usage stats
    view_count = Column(Integer, default=0)
    completion_rate = Column(Float)
    average_rating = Column(Float)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# ============= Analytics Models =============

class UserActivity(Base):
    """Track user activity for analytics"""
    __tablename__ = "user_activity"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    activity_type = Column(String(50), nullable=False)  # login, query, view_stock, etc.
    activity_data = Column(JSON)

    # Session info
    session_id = Column(String, index=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_user_activity', 'user_id', 'activity_type', 'created_at'),
    )

class QueryAnalytics(Base):
    """Analytics on user queries"""
    __tablename__ = "query_analytics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    query_text = Column(Text, nullable=False)
    query_type = Column(String(50))  # stock, education, planning, etc.

    # Performance metrics
    response_time = Column(Float)
    tokens_used = Column(Integer)
    model_used = Column(String(50))
    confidence_score = Column(Float)

    # User feedback
    was_helpful = Column(Boolean)
    user_rating = Column(Integer)

    # Metadata
    entities_detected = Column(JSON)  # Stocks, topics, etc.
    data_sources_used = Column(JSON)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_query_type', 'query_type', 'created_at'),
    )