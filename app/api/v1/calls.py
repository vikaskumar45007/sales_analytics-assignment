import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.database import get_db
from app.models.call import Call
from app.schemas.call import (
    CallResponse, CallCreate, CallUpdate, CallListParams, CallRecommendations,
    SimilarCall, CoachingRecommendation, ErrorResponse
)
from app.services.ai_insights import AIInsightsService
from app.utils.auth import get_current_active_user, require_manager, require_agent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calls", tags=["calls"])

ai_service = AIInsightsService()


@router.post("", response_model=CallResponse, status_code=201)
async def create_call(
    call_data: CallCreate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_manager)
):
    """Create a new call"""
    try:
        existing_call = db.query(Call).filter(Call.call_id == call_data.call_id).first()
        if existing_call:
            raise HTTPException(status_code=400, detail="Call with this ID already exists")
        
        call = Call(
            call_id=call_data.call_id,
            agent_id=call_data.agent_id,
            customer_id=call_data.customer_id,
            language=call_data.language,
            start_time=call_data.start_time,
            duration_seconds=call_data.duration_seconds,
            transcript=call_data.transcript
        )
        
        db.add(call)
        db.commit()
        db.refresh(call)
        
        return call
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating call: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/bulk", response_model=List[CallResponse], status_code=201)
async def create_calls_bulk(
    calls_data: List[CallCreate], 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_manager)
):
    """Create multiple calls at once"""
    try:
        created_calls = []
        
        for call_data in calls_data:
            existing_call = db.query(Call).filter(Call.call_id == call_data.call_id).first()
            if existing_call:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Call with ID {call_data.call_id} already exists"
                )
            
            call = Call(
                call_id=call_data.call_id,
                agent_id=call_data.agent_id,
                customer_id=call_data.customer_id,
                language=call_data.language,
                start_time=call_data.start_time,
                duration_seconds=call_data.duration_seconds,
                transcript=call_data.transcript
            )
            
            db.add(call)
            created_calls.append(call)
        
        db.commit()
        
        for call in created_calls:
            db.refresh(call)
        
        return created_calls
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating calls in bulk: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=List[CallResponse])
async def list_calls(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    agent_id: str = Query(None),
    from_date: str = Query(None),
    to_date: str = Query(None),
    min_sentiment: float = Query(None, ge=-1, le=1),
    max_sentiment: float = Query(None, ge=-1, le=1),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """List calls with filtering and pagination"""
    try:
        query = db.query(Call)
        
        if agent_id:
            query = query.filter(Call.agent_id == agent_id)
            
        if from_date:
            from datetime import datetime
            from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            query = query.filter(Call.start_time >= from_dt)
            
        if to_date:
            from datetime import datetime
            to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            query = query.filter(Call.start_time <= to_dt)
            
        if min_sentiment is not None:
            query = query.filter(Call.customer_sentiment_score >= min_sentiment)
            
        if max_sentiment is not None:
            query = query.filter(Call.customer_sentiment_score <= max_sentiment)
        
        query = query.order_by(desc(Call.start_time))
        
        calls = query.offset(offset).limit(limit).all()
        
        return calls
        
    except Exception as e:
        logger.error(f"Error listing calls: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: str, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get detailed information for a specific call"""
    call = db.query(Call).filter(Call.call_id == call_id).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return call


@router.put("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: str, 
    call_update: CallUpdate, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_manager)
):
    """Update a call with AI insights"""
    call = db.query(Call).filter(Call.call_id == call_id).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    try:
        if call_update.agent_talk_ratio is not None:
            call.agent_talk_ratio = call_update.agent_talk_ratio
        if call_update.customer_sentiment_score is not None:
            call.customer_sentiment_score = call_update.customer_sentiment_score
        if call_update.embeddings is not None:
            call.embeddings = call_update.embeddings
        
        db.commit()
        db.refresh(call)
        
        return call
        
    except Exception as e:
        logger.error(f"Error updating call {call_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{call_id}/process", response_model=CallResponse)
async def process_call_with_ai(
    call_id: str, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_manager)
):
    """Process a call with AI insights"""
    call = db.query(Call).filter(Call.call_id == call_id).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    try:
        insights = ai_service.process_call(call)
        
        if insights.get('agent_talk_ratio') is not None:
            call.agent_talk_ratio = insights['agent_talk_ratio']
        if insights.get('customer_sentiment_score') is not None:
            call.customer_sentiment_score = insights['customer_sentiment_score']
        if insights.get('embeddings') is not None:
            call.embeddings = insights['embeddings']
        
        db.commit()
        db.refresh(call)
        
        return call
        
    except Exception as e:
        logger.error(f"Error processing call {call_id} with AI: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{call_id}/recommendations", response_model=CallRecommendations)
async def get_call_recommendations(
    call_id: str, 
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get similar calls and coaching recommendations"""
    
    target_call = db.query(Call).filter(Call.call_id == call_id).first()
    
    if not target_call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    if not target_call.embeddings:
        raise HTTPException(
            status_code=400, 
            detail="Call embeddings not available"
        )
    
    try:
        all_calls = db.query(Call).filter(
            and_(
                Call.call_id != call_id,
                Call.embeddings.isnot(None)
            )
        ).all()
        
        similarities = []
        for call in all_calls:
            if call.embeddings:
                similarity = ai_service.calculate_cosine_similarity(
                    target_call.embeddings, call.embeddings
                )
                similarities.append({
                    'call': call,
                    'similarity': similarity
                })
        
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        top_similar = similarities[:5]
        
        similar_calls = [
            SimilarCall(
                call_id=item['call'].call_id,
                agent_id=item['call'].agent_id,
                similarity_score=item['similarity'],
                customer_sentiment_score=item['call'].customer_sentiment_score,
                start_time=item['call'].start_time
            )
            for item in top_similar
        ]
        
        coaching_nudges_data = await ai_service.generate_coaching_recommendations(
            call_id, [item['call'] for item in top_similar]
        )
        coaching_nudges = []
        for nudge in coaching_nudges_data:
            try:
                if len(nudge.get('suggestion', '')) > 100:
                    nudge['suggestion'] = nudge['suggestion'][:97] + "..."
                
                coaching_nudge = CoachingRecommendation(**nudge)
                coaching_nudges.append(coaching_nudge)
            except Exception as e:
                logger.warning(f"Invalid coaching recommendation: {e}, skipping...")
                continue
        
        if not coaching_nudges:
            logger.info(f"No valid coaching recommendations generated for {call_id}, using defaults")
            coaching_nudges = [
                CoachingRecommendation(title="Active Listening", suggestion="Ask more follow-up questions to better understand customer needs."),
                CoachingRecommendation(title="Empathy Building", suggestion="Acknowledge customer frustrations before offering solutions."),
                CoachingRecommendation(title="Solution Focus", suggestion="Provide clear next steps and timeline for resolution.")
            ]
        
        return CallRecommendations(
            call_id=call_id,
            similar_calls=similar_calls,
            coaching_nudges=coaching_nudges
        )
        
    except Exception as e:
        logger.error(f"Error generating recommendations for {call_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")