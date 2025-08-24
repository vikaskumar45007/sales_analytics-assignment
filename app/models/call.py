from datetime import datetime
from typing import Optional, List
import uuid
from sqlalchemy import (
    Column, String, DateTime, Float, Integer, Text, 
    JSON, Index, text
)
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Call(Base):
    __tablename__ = "calls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(String(100), unique=True, nullable=False, index=True)
    agent_id = Column(String(100), nullable=False, index=True)
    customer_id = Column(String(100), nullable=False)
    language = Column(String(10), nullable=False, default="en")
    start_time = Column(DateTime, nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=False)
    transcript = Column(Text, nullable=False)
    
    agent_talk_ratio = Column(Float)
    customer_sentiment_score = Column(Float)
    embeddings = Column(JSON)  
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    search_vector = Column(TSVECTOR)
    
    __table_args__ = (
        Index('idx_calls_search', 'search_vector', postgresql_using='gin'),
        Index('idx_calls_agent_time', 'agent_id', 'start_time'),
        Index('idx_calls_sentiment', 'customer_sentiment_score'),
    )


class CallAnalytics(Base):
    """Precomputed analytics cache"""
    __tablename__ = "call_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(100), nullable=False, unique=True)
    total_calls = Column(Integer, default=0)
    avg_sentiment = Column(Float)
    avg_talk_ratio = Column(Float)
    last_updated = Column(DateTime, default=func.now())