import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.call import Call
from app.schemas.call import AgentAnalytics
from app.utils.auth import get_current_active_user, require_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/agents", response_model=List[AgentAnalytics])
async def get_agent_leaderboard(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_manager)
):
    """Get agent performance leaderboard"""
    try:

        results = db.query(
            Call.agent_id,
            func.count(Call.id).label('total_calls'),
            func.avg(Call.customer_sentiment_score).label('avg_sentiment'),
            func.avg(Call.agent_talk_ratio).label('avg_talk_ratio')
        ).group_by(Call.agent_id).all()
        
        agent_analytics = []
        for result in results:
            analytics = AgentAnalytics(
                agent_id=result.agent_id,
                total_calls=result.total_calls,
                avg_sentiment=float(result.avg_sentiment) if result.avg_sentiment else None,
                avg_talk_ratio=float(result.avg_talk_ratio) if result.avg_talk_ratio else None
            )
            agent_analytics.append(analytics)
        

        agent_analytics.sort(
            key=lambda x: x.avg_sentiment or -2, 
            reverse=True
        )
        
        return agent_analytics
        
    except Exception as e:
        logger.error(f"Error generating agent analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")