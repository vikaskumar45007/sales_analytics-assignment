import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from faker import Faker
import random
from app.models.call import Call
from app.database import SessionLocal
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
fake = Faker()


class DataIngestion:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    async def generate_synthetic_transcripts(self, count: int = 200) -> List[Dict[str, Any]]:
        """Generate synthetic call transcripts"""
        logger.info(f"Generating {count} synthetic transcripts...")
        
        transcripts = []
        agent_pool = [f"agent_{i:03d}" for i in range(1, 21)]  # 20 agents
        
        for i in range(count):
            start_time = fake.date_time_between(
                start_date='-30d', 
                end_date='now'
            )
            duration = random.randint(180, 1800)  # 3-30 minutes
            
            # Generate conversation
            transcript_parts = []
            num_exchanges = random.randint(5, 15)
            
            for j in range(num_exchanges):
                if j % 2 == 0:  # Agent speaks
                    agent_line = self._generate_agent_response()
                    transcript_parts.append(f"Agent: {agent_line}")
                else:  # Customer speaks
                    customer_line = self._generate_customer_response()
                    transcript_parts.append(f"Customer: {customer_line}")
            
            transcript = "\n".join(transcript_parts)
            
            call_data = {
                "call_id": f"call_{i:06d}",
                "agent_id": random.choice(agent_pool),
                "customer_id": f"customer_{fake.uuid4()[:8]}",
                "language": "en",
                "start_time": start_time.isoformat(),
                "duration_seconds": duration,
                "transcript": transcript
            }
            
            transcripts.append(call_data)
            
        # Save raw data
        raw_file = self.data_dir / "synthetic_transcripts.json"
        with open(raw_file, 'w') as f:
            json.dump(transcripts, f, indent=2, default=str)
            
        logger.info(f"Saved {count} transcripts to {raw_file}")
        return transcripts
    
    def _generate_agent_response(self) -> str:
        """Generate realistic agent responses"""
        responses = [
            "Thank you for calling. How can I assist you today?",
            "I understand your concern. Let me check that for you.",
            "I apologize for the inconvenience. Let me see what I can do.",
            "That's a great question. Based on your account, I can see that...",
            "I'd be happy to help you with that. Can you provide me with...",
            "Let me transfer you to our specialist team for better assistance.",
            "I've updated your account. Is there anything else I can help with?",
            "Thank you for your patience. I found the information you need.",
        ]
        return random.choice(responses)
    
    def _generate_customer_response(self) -> str:
        """Generate realistic customer responses"""
        responses = [
            "Hi, I'm having trouble with my recent order.",
            "Yes, I've been waiting for a refund for two weeks now.",
            "That doesn't sound right. Can you check again?",
            "I'm really frustrated with this service.",
            "Thank you so much for your help!",
            "Can you explain why this happened?",
            "I need to speak with a manager about this.",
            "That resolves my issue. I appreciate your assistance.",
        ]
        return random.choice(responses)
    
    async def ingest_to_database(self, transcripts: List[Dict[str, Any]]):
        """Store transcripts in database"""
        logger.info(f"Ingesting {len(transcripts)} transcripts to database...")
        
        db = SessionLocal()
        try:
            for transcript_data in transcripts:
                # Convert ISO string back to datetime
                transcript_data["start_time"] = datetime.fromisoformat(
                    transcript_data["start_time"].replace('Z', '+00:00')
                )
                
                call = Call(**transcript_data)
                db.add(call)
                
            db.commit()
            logger.info("Successfully ingested all transcripts")
            
        except Exception as e:
            logger.error(f"Error ingesting transcripts: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def run_ingestion_pipeline(self, count: int = 200):
        """Run complete ingestion pipeline"""
        try:
            # Generate synthetic data
            transcripts = await self.generate_synthetic_transcripts(count)
            
            # to database
            await self.ingest_to_database(transcripts)
            
            logger.info("Ingestion pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"Ingestion pipeline failed: {e}")
            raise


async def main():
    """CLI entry point for data ingestion"""
    logging.basicConfig(level=logging.INFO)
    
    ingestion = DataIngestion()
    await ingestion.run_ingestion_pipeline(200)


if __name__ == "__main__":
    asyncio.run(main())