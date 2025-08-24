import asyncio
import json
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.call import Call
from app.services.ai_insights import AIInsightsService
from app.utils.auth import AuthService

logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, call_id: str):
        """Connect a WebSocket to a specific call"""
        await websocket.accept()
        if call_id not in self.active_connections:
            self.active_connections[call_id] = []
        self.active_connections[call_id].append(websocket)
        logger.info(f"WebSocket connected to call {call_id}")
    
    def disconnect(self, websocket: WebSocket, call_id: str):
        """Disconnect a WebSocket from a call"""
        if call_id in self.active_connections:
            self.active_connections[call_id].remove(websocket)
            if not self.active_connections[call_id]:
                del self.active_connections[call_id]
        logger.info(f"WebSocket disconnected from call {call_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        await websocket.send_text(message)
    
    async def broadcast_to_call(self, message: str, call_id: str):
        """Broadcast message to all connections for a specific call"""
        if call_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[call_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to WebSocket: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(connection, call_id)


# Global connection manager
manager = ConnectionManager()

# AI service for sentiment analysis
ai_service = AIInsightsService()


class SentimentStreamer:
    """Real-time sentiment streaming service"""
    
    def __init__(self):
        self.streaming_calls: Dict[str, bool] = {}
        self.sentiment_history: Dict[str, List[Dict]] = {}
    
    async def start_streaming(self, call_id: str, db: Session):
        """Start real-time sentiment streaming for a call"""
        if call_id in self.streaming_calls and self.streaming_calls[call_id]:
            return  # Already streaming
        
        self.streaming_calls[call_id] = True
        self.sentiment_history[call_id] = []
        
        logger.info(f"Starting sentiment streaming for call {call_id}")
        
        # Start streaming task
        asyncio.create_task(self._stream_sentiment(call_id, db))
    
    def stop_streaming(self, call_id: str):
        """Stop sentiment streaming for a call"""
        self.streaming_calls[call_id] = False
        logger.info(f"Stopped sentiment streaming for call {call_id}")
    
    async def _stream_sentiment(self, call_id: str, db: Session):
        """Stream sentiment data in real-time"""
        try:
            # Get call data
            call = db.query(Call).filter(Call.call_id == call_id).first()
            if not call:
                logger.error(f"Call {call_id} not found")
                return
            
            # Simulate real-time sentiment updates
            # In production, this would connect to live audio stream
            base_sentiment = 0.0
            timestamp = datetime.utcnow()
            
            while self.streaming_calls.get(call_id, False):
                # Simulate sentiment fluctuations
                sentiment_change = random.uniform(-0.1, 0.1)
                base_sentiment = max(-1.0, min(1.0, base_sentiment + sentiment_change))
                
                # Create sentiment data
                sentiment_data = {
                    "call_id": call_id,
                    "timestamp": timestamp.isoformat(),
                    "sentiment_score": round(base_sentiment, 3),
                    "confidence": random.uniform(0.7, 0.95),
                    "emotion": self._get_emotion_from_sentiment(base_sentiment),
                    "intensity": abs(base_sentiment)
                }
                
                # Add to history
                self.sentiment_history[call_id].append(sentiment_data)
                
                # Broadcast to all connected clients
                await manager.broadcast_to_call(
                    json.dumps({
                        "type": "sentiment_update",
                        "data": sentiment_data
                    }),
                    call_id
                )
                
                # Update timestamp
                timestamp = datetime.utcnow()
                
                # Wait before next update (simulate real-time)
                await asyncio.sleep(2)  # 2-second intervals
                
        except Exception as e:
            logger.error(f"Error in sentiment streaming for call {call_id}: {e}")
        finally:
            self.stop_streaming(call_id)
    
    def _get_emotion_from_sentiment(self, sentiment: float) -> str:
        """Convert sentiment score to emotion label"""
        if sentiment >= 0.6:
            return "very_positive"
        elif sentiment >= 0.2:
            return "positive"
        elif sentiment >= -0.2:
            return "neutral"
        elif sentiment >= -0.6:
            return "negative"
        else:
            return "very_negative"
    
    def get_sentiment_history(self, call_id: str) -> List[Dict]:
        """Get sentiment history for a call"""
        return self.sentiment_history.get(call_id, [])


# Global sentiment streamer
sentiment_streamer = SentimentStreamer()


async def authenticate_websocket(websocket: WebSocket) -> Optional[str]:
    """Authenticate WebSocket connection using token"""
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            return None
        
        # Verify token
        payload = AuthService.verify_token(token)
        if not payload:
            await websocket.close(code=4001, reason="Invalid authentication token")
            return None
        
        return payload.get("sub")  # Return username
    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        return None


async def websocket_sentiment_endpoint(
    websocket: WebSocket,
    call_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time sentiment streaming"""
    try:
        # Authenticate connection
        username = await authenticate_websocket(websocket)
        if not username:
            return
        
        # Connect to call
        await manager.connect(websocket, call_id)
        
        # Verify call exists
        call = db.query(Call).filter(Call.call_id == call_id).first()
        if not call:
            await manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "message": f"Call {call_id} not found"
                }),
                websocket
            )
            return
        
        # Send initial connection message
        await manager.send_personal_message(
            json.dumps({
                "type": "connection_established",
                "call_id": call_id,
                "message": "Connected to real-time sentiment stream"
            }),
            websocket
        )
        
        # Start sentiment streaming if not already running
        await sentiment_streamer.start_streaming(call_id, db)
        
        # Send sentiment history
        history = sentiment_streamer.get_sentiment_history(call_id)
        if history:
            await manager.send_personal_message(
                json.dumps({
                    "type": "sentiment_history",
                    "data": history
                }),
                websocket
            )
        
        # Keep connection alive and handle messages
        try:
            while True:
                # Wait for client messages (ping/pong, commands, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong"}),
                        websocket
                    )
                elif message.get("type") == "get_history":
                    history = sentiment_streamer.get_sentiment_history(call_id)
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "sentiment_history",
                            "data": history
                        }),
                        websocket
                    )
                elif message.get("type") == "stop_streaming":
                    sentiment_streamer.stop_streaming(call_id)
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "streaming_stopped",
                            "message": "Sentiment streaming stopped"
                        }),
                        websocket
                    )
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for call {call_id}")
        except Exception as e:
            logger.error(f"WebSocket error for call {call_id}: {e}")
            await manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "message": "Internal server error"
                }),
                websocket
            )
    
    except Exception as e:
        logger.error(f"WebSocket endpoint error: {e}")
    finally:
        # Clean up connection
        manager.disconnect(websocket, call_id)
