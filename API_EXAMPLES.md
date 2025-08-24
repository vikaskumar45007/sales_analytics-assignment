# API Examples

This document shows how to use the Sales Analytics API endpoints.

## Authentication

All API endpoints (except login) require JWT authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your_jwt_token>
```

### Login to get JWT token

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Register new user (admin only)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_token>" \
  -d '{
    "username": "newagent",
    "email": "newagent@company.com",
    "password": "securepassword",
    "role": "agent"
  }'
```

### Get current user info

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <your_token>"
```

### Refresh token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Authorization: Bearer <your_token>"
```

## Base URL
```
http://localhost:8000/api/v1
```

## Adding Calls

### 1. Add a Single Call

```bash
curl -X POST "http://localhost:8000/api/v1/calls" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "call_id": "call-001",
    "agent_id": "agent-001",
    "customer_id": "customer-001",
    "language": "en",
    "start_time": "2024-01-15T10:00:00Z",
    "duration_seconds": 300,
    "transcript": "Agent: Hello, how can I help you today?\nCustomer: I have a question about my account.\nAgent: I would be happy to help with that."
  }'
```

### 2. Add Multiple Calls (Bulk)

```bash
curl -X POST "http://localhost:8000/api/v1/calls/bulk" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '[
    {
      "call_id": "call-002",
      "agent_id": "agent-002",
      "customer_id": "customer-002",
      "language": "en",
      "start_time": "2024-01-15T11:00:00Z",
      "duration_seconds": 450,
      "transcript": "Agent: Good morning! How may I assist you?\nCustomer: I need help with my subscription.\nAgent: I can certainly help with that."
    },
    {
      "call_id": "call-003",
      "agent_id": "agent-001",
      "customer_id": "customer-003",
      "language": "en",
      "start_time": "2024-01-15T12:00:00Z",
      "duration_seconds": 600,
      "transcript": "Agent: Hello! Thank you for calling.\nCustomer: Hi, I want to upgrade my plan.\nAgent: Great! Let me help you with that upgrade."
    }
  ]'
```

## Retrieving Calls

### 1. List All Calls

```bash
curl "http://localhost:8000/api/v1/calls" \
  -H "Authorization: Bearer <your_token>"
```

### 2. List Calls with Pagination

```bash
curl "http://localhost:8000/api/v1/calls?limit=5&offset=0"
```

### 3. Filter Calls by Agent

```bash
curl "http://localhost:8000/api/v1/calls?agent_id=agent-001"
```

### 4. Filter Calls by Date Range

```bash
curl "http://localhost:8000/api/v1/calls?from_date=2024-01-15T00:00:00Z&to_date=2024-01-15T23:59:59Z"
```

### 5. Filter Calls by Sentiment

```bash
curl "http://localhost:8000/api/v1/calls?min_sentiment=0.5"
```

### 6. Get Specific Call

```bash
curl "http://localhost:8000/api/v1/calls/call-001"
```

## Processing Calls with AI

### 1. Process a Call with AI Insights

```bash
curl -X POST "http://localhost:8000/api/v1/calls/call-001/process" \
  -H "Authorization: Bearer <your_token>"
```

### 2. Update Call with AI Insights Manually

```bash
curl -X PUT "http://localhost:8000/api/v1/calls/call-001" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_talk_ratio": 0.6,
    "customer_sentiment_score": 0.8,
    "embeddings": [0.1, 0.2, 0.3, 0.4, 0.5]
  }'
```

## Getting Recommendations

### 1. Get Call Recommendations

```bash
curl "http://localhost:8000/api/v1/calls/call-001/recommendations"
```

## Analytics

### 1. Get Agent Analytics

```bash
curl "http://localhost:8000/api/v1/analytics/agents"
```

## Using the Sample Data Script

### 1. Run the Sample Data Generator

```bash
python3 add_sample_calls.py
```

This will:
- Add 5 sample calls to your database
- Process them with AI insights (if AI models are available)
- Show you the results

## Python Examples

### 1. Add a Call using Python

```python
import requests
import json

# Add a single call
call_data = {
    "call_id": "python-call-001",
    "agent_id": "agent-001",
    "customer_id": "customer-001",
    "language": "en",
    "start_time": "2024-01-15T10:00:00Z",
    "duration_seconds": 300,
    "transcript": "Agent: Hello\nCustomer: Hi there\nAgent: How can I help?"
}

response = requests.post(
    "http://localhost:8000/api/v1/calls",
    json=call_data,
    headers={"Content-Type": "application/json"}
)

if response.status_code == 201:
    print("Call added successfully!")
    print(response.json())
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### 2. Get All Calls

```python
import requests

response = requests.get("http://localhost:8000/api/v1/calls")
calls = response.json()

print(f"Total calls: {len(calls)}")
for call in calls:
    print(f"- {call['call_id']} (Agent: {call['agent_id']})")
```

### 3. Process Calls with AI

```python
import requests

# Process a call with AI
response = requests.post("http://localhost:8000/api/v1/calls/call-001/process")
if response.status_code == 200:
    processed_call = response.json()
    print(f"Sentiment: {processed_call['customer_sentiment_score']}")
    print(f"Talk Ratio: {processed_call['agent_talk_ratio']}")
```

## Common Response Codes

- `200` - Success (GET, PUT)
- `201` - Created (POST)
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `500` - Internal Server Error

## Error Handling

All endpoints return JSON error responses:

```json
{
  "detail": "Error message here"
}
```

## Notes

1. **Call IDs must be unique** - You cannot create two calls with the same `call_id`
2. **Duration must be positive** - `duration_seconds` must be greater than 0
3. **Sentiment scores range from -1 to 1** - Negative values indicate negative sentiment
4. **AI processing is optional** - Calls work without AI insights, but recommendations require embeddings
5. **Date format** - Use ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`

## WebSocket Real-time Sentiment Streaming

### Connect to WebSocket

```bash
# Using wscat (install with: npm install -g wscat)
wscat -c "ws://localhost:8000/ws/sentiment/call-001?token=<your_jwt_token>"

# Using Python websockets
python websocket_test_client.py call-001 <your_jwt_token>
```

### WebSocket Messages

**Sentiment Updates (from server):**
```json
{
  "type": "sentiment_update",
  "data": {
    "call_id": "call-001",
    "timestamp": "2024-01-15T10:30:00.123456",
    "sentiment_score": 0.75,
    "confidence": 0.89,
    "emotion": "positive",
    "intensity": 0.75
  }
}
```

**Client Commands (to server):**
```json
{"type": "ping"}
{"type": "get_history"}
{"type": "stop_streaming"}
```

### Python WebSocket Client Example

```python
import asyncio
import websockets
import json

async def connect_to_sentiment_stream(call_id: str, token: str):
    uri = f"ws://localhost:8000/ws/sentiment/{call_id}?token={token}"
    
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "sentiment_update":
                sentiment = data["data"]["sentiment_score"]
                emotion = data["data"]["emotion"]
                print(f"Sentiment: {sentiment} ({emotion})")

# Usage
asyncio.run(connect_to_sentiment_stream("call-001", "your_jwt_token"))
```
