# Sales Call Analytics

This project is a Python microservice designed to ingest sales call transcripts, store them durably, and provide actionable conversation analytics through a REST API. The service leverages FastAPI for the API layer, SQLAlchemy for database interactions, and various AI models for generating insights from the transcripts.

## Features

- **Data Ingestion**: Asynchronously ingests sales call transcripts from various sources, including openly licensed datasets or synthetic generation.
- **Durable Storage**: Utilizes PostgreSQL (or SQLite for local development) to store call transcripts and analytics data.
- **AI Insights**: Computes sentence embeddings and performs sentiment analysis on the transcripts to derive actionable insights.
- **REST API**: Provides endpoints for retrieving call data, analytics, and recommendations based on conversation metrics.
- **JWT Authentication**: Secure authentication with role-based access control (admin, manager, agent roles).
- **Real-time Updates**: WebSocket connections for streaming real-time sentiment analysis during calls.
- **Role-based Authorization**: Different access levels for different user roles.

## Project Structure

```
sales-call-analytics
├── app
│   ├── api                # API routes for handling requests
│   ├── db                 # Database models and session management
│   ├── ingestion           # Data ingestion pipeline
│   ├── ai                 # AI models for embeddings and sentiment analysis
│   ├── schemas            # Pydantic models for request/response validation
│   ├── services           # Business logic for analytics
│   ├── auth               # Authentication middleware
│   ├── websocket          # WebSocket endpoints for real-time updates
│   └── main.py           # Entry point for the application
├── tests                  # Unit tests for various components
├── alembic.ini           # Alembic migrations configuration
├── Dockerfile             # Docker image build instructions
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Project dependencies
├── pre-commit-config.yaml # Pre-commit hooks configuration
├── .github
│   └── workflows
│       └── ci.yml        # CI workflow for testing and building
├── README.md              # Project documentation
└── .env.example           # Example environment configuration
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd sales-call-analytics
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database and run migrations:
   ```
   alembic upgrade head
   ```

5. Start the application:
   ```
   uvicorn app.main:app --reload
   ```

## Authentication

The application uses JWT authentication with role-based access control:

### Default Users
- **Admin**: `admin` / `admin123` (full access)
- **Manager**: `manager1` / `manager123` (manager access)
- **Agent**: `agent1` / `agent123` (agent access)

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Using Authentication
Include the JWT token in the Authorization header:
```bash
Authorization: Bearer <your_jwt_token>
```

## Usage

- Access the API documentation at `http://localhost:8000/docs`.
- Use the provided endpoints to interact with the sales call data and analytics.

### WebSocket Real-time Sentiment

Connect to real-time sentiment streaming:

```bash
# Using the provided test client
python websocket_test_client.py call-001 <your_jwt_token>

# Using wscat
wscat -c "ws://localhost:8000/ws/sentiment/call-001?token=<your_jwt_token>"
```

### API Examples

See `API_EXAMPLES.md` for comprehensive examples of all endpoints.

