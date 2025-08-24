#!/usr/bin/env python3
"""
Script to add sample calls to the database for testing.
This script creates sample call data and adds it to the database.
"""

import requests
import json
from datetime import datetime, timedelta
import random

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def create_sample_calls():
    """Create sample call data"""
    sample_calls = [
        {
            "call_id": "call-001",
            "agent_id": "agent-001",
            "customer_id": "customer-001",
            "language": "en",
            "start_time": (datetime.now() - timedelta(hours=2)).isoformat() + "Z",
            "duration_seconds": 300,
            "transcript": """
Agent: Hello, thank you for calling our support line. How can I help you today?
Customer: Hi, I'm having trouble with my account login.
Agent: I understand that can be frustrating. Let me help you resolve this issue.
Customer: Thank you, I've been trying for hours.
Agent: I'll get this sorted out for you right away. Can you tell me your username?
Customer: Yes, it's john.doe@example.com
Agent: Perfect, I can see your account. Let me reset your password for you.
Customer: That would be great, thank you so much!
Agent: You're welcome! I've sent a reset link to your email.
Customer: Excellent, I really appreciate your help.
Agent: Is there anything else I can assist you with today?
Customer: No, that's all I needed. Thank you again!
Agent: You're very welcome. Have a great day!
            """.strip()
        },
        {
            "call_id": "call-002",
            "agent_id": "agent-002",
            "customer_id": "customer-002",
            "language": "en",
            "start_time": (datetime.now() - timedelta(hours=1)).isoformat() + "Z",
            "duration_seconds": 450,
            "transcript": """
Agent: Good morning! Welcome to our service. How may I assist you?
Customer: Hi, I need to cancel my subscription.
Agent: I'm sorry to hear that. Can you tell me why you're considering cancellation?
Customer: I'm not satisfied with the service quality.
Agent: I understand your concern. Let me see what we can do to improve your experience.
Customer: I've been a customer for 2 years and the quality has declined.
Agent: That's not acceptable. Let me offer you a discount and escalate your feedback.
Customer: Really? That would be helpful.
Agent: Absolutely. I'm applying a 50% discount for the next 3 months.
Customer: Wow, thank you! That's very generous.
Agent: And I'm personally following up on your quality concerns.
Customer: I appreciate that. Maybe I'll reconsider the cancellation.
Agent: I hope so. Your satisfaction is our priority.
            """.strip()
        },
        {
            "call_id": "call-003",
            "agent_id": "agent-001",
            "customer_id": "customer-003",
            "language": "en",
            "start_time": datetime.now().isoformat() + "Z",
            "duration_seconds": 600,
            "transcript": """
Agent: Hello! Thank you for calling. How can I help you today?
Customer: Hi, I want to upgrade my plan.
Agent: Great! I'd be happy to help you upgrade. What features are you looking for?
Customer: I need more storage and better support.
Agent: Perfect! We have several upgrade options. Let me show you the best ones.
Customer: That sounds good. What are the prices?
Agent: Our premium plan is $29/month and includes 1TB storage and priority support.
Customer: That's reasonable. What about the enterprise plan?
Agent: The enterprise plan is $99/month with unlimited storage and 24/7 support.
Customer: I think the premium plan would work for me.
Agent: Excellent choice! Let me process that upgrade for you right now.
Customer: Thank you! This is exactly what I needed.
Agent: You're welcome! Your upgrade is complete. You'll see the new features immediately.
Customer: Perfect! I'm very happy with this service.
Agent: I'm glad I could help! Is there anything else you need?
Customer: No, that's everything. Thank you so much!
Agent: You're very welcome! Have a wonderful day!
            """.strip()
        },
        {
            "call_id": "call-004",
            "agent_id": "agent-003",
            "customer_id": "customer-004",
            "language": "en",
            "start_time": (datetime.now() - timedelta(minutes=30)).isoformat() + "Z",
            "duration_seconds": 180,
            "transcript": """
Agent: Hello, how can I help you today?
Customer: I'm very angry about your service!
Agent: I understand you're frustrated. Let me help resolve this for you.
Customer: You better fix this or I'm going to complain everywhere!
Agent: I want to help you. Can you tell me what happened?
Customer: My data was lost and you're not responding to my emails!
Agent: That's serious and I apologize. Let me escalate this immediately.
Customer: You should be sorry! This is unacceptable!
Agent: You're absolutely right. Let me get a supervisor on the line right now.
Customer: Fine, but this better be resolved today!
Agent: I'm transferring you to a supervisor who can help immediately.
            """.strip()
        },
        {
            "call_id": "call-005",
            "agent_id": "agent-002",
            "customer_id": "customer-005",
            "language": "en",
            "start_time": (datetime.now() - timedelta(minutes=15)).isoformat() + "Z",
            "duration_seconds": 240,
            "transcript": """
Agent: Good afternoon! How may I assist you today?
Customer: Hi, I have a question about billing.
Agent: I'd be happy to help with your billing question. What would you like to know?
Customer: I was charged twice this month.
Agent: I can see the duplicate charge. Let me fix that for you right away.
Customer: Thank you! I was worried about that.
Agent: No problem at all. I've issued a refund for the duplicate charge.
Customer: That's great! How long will it take to process?
Agent: The refund will appear in your account within 3-5 business days.
Customer: Perfect, thank you for your help.
Agent: You're welcome! Is there anything else I can help you with?
Customer: No, that's all I needed. Have a great day!
Agent: You too! Thank you for calling.
            """.strip()
        }
    ]
    
    return sample_calls

def add_calls_to_database():
    """Add sample calls to the database via API"""
    sample_calls = create_sample_calls()
    
    print("Adding sample calls to the database...")
    
    for i, call_data in enumerate(sample_calls, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/calls",
                json=call_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                print(f"✅ Added call {i}: {call_data['call_id']}")
            else:
                print(f"❌ Failed to add call {i}: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed to connect to API. Make sure the server is running on {BASE_URL}")
            return False
        except Exception as e:
            print(f"❌ Error adding call {i}: {e}")
    
    return True

def process_calls_with_ai():
    """Process calls with AI insights"""
    print("\nProcessing calls with AI insights...")
    
    call_ids = ["call-001", "call-002", "call-003", "call-004", "call-005"]
    
    for call_id in call_ids:
        try:
            response = requests.post(f"{BASE_URL}/calls/{call_id}/process")
            
            if response.status_code == 200:
                print(f"✅ Processed call: {call_id}")
            else:
                print(f"❌ Failed to process call {call_id}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error processing call {call_id}: {e}")

def check_calls():
    """Check the calls in the database"""
    try:
        response = requests.get(f"{BASE_URL}/calls")
        
        if response.status_code == 200:
            calls = response.json()
            print(f"\n📊 Total calls in database: {len(calls)}")
            
            if calls:
                print("\nRecent calls:")
                for call in calls[:3]:  # Show first 3 calls
                    print(f"  - {call['call_id']} (Agent: {call['agent_id']}, Duration: {call['duration_seconds']}s)")
        else:
            print(f"❌ Failed to get calls: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking calls: {e}")

def main():
    print("🚀 Sales Analytics - Sample Data Generator")
    print("=" * 50)
    
    # Add sample calls
    if add_calls_to_database():
        print("\n✅ Sample calls added successfully!")
        
        # Check calls
        check_calls()
        
        # Process with AI (optional - requires AI models)
        print("\n🤖 AI Processing (optional - requires AI models)")
        process_calls_with_ai()
        
        print("\n🎉 Setup complete!")
        print(f"📖 View your calls at: {BASE_URL}/calls")
        print(f"📊 View analytics at: {BASE_URL}/analytics/agents")
    else:
        print("\n❌ Failed to add sample calls")

if __name__ == "__main__":
    main()
