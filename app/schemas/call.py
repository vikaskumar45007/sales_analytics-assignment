from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
import uuid


class CallBase(BaseModel):
    call_id: str
    agent_id: str  
    customer_id: str
    language: str = "en"
    start_time: datetime
    duration_seconds: int = Field(gt=0)
    transcript: str


class CallCreate(CallBase):
    pass


class CallUpdate(BaseModel):
    agent_talk_ratio: Optional[float] = None
    customer_sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    embeddings: Optional[List[float]] = None


class CallResponse(CallBase):
    id: uuid.UUID
    agent_talk_ratio: Optional[float] = None
    customer_sentiment_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CallListParams(BaseModel):
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)
    agent_id: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    min_sentiment: Optional[float] = Field(None, ge=-1, le=1)
    max_sentiment: Optional[float] = Field(None, ge=-1, le=1)


class SimilarCall(BaseModel):
    call_id: str
    agent_id: str
    similarity_score: float
    customer_sentiment_score: Optional[float]
    start_time: datetime


class CoachingRecommendation(BaseModel):
    title: str
    suggestion: str = Field(max_length=500)  # Increased from 40 to 500 

class CallRecommendations(BaseModel):
    call_id: str
    similar_calls: List[SimilarCall]
    coaching_nudges: List[CoachingRecommendation]


class AgentAnalytics(BaseModel):
    agent_id: str
    total_calls: int
    avg_sentiment: Optional[float]
    avg_talk_ratio: Optional[float]
    
    
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None