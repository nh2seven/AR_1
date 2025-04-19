# Analytics & Reporting - 1
- A microservices-based platform designed for backend developers to track, analyze, and report user progress and performance in virtual laboratory environments.
- This repository is not designed for end-user interaction, and is not in production yet.

## Services
### User Progress Service (Port: 8004)
Tracks individual user progress and attempts in virtual lab exercises:
- Records lab attempts and completion status
- Tracks time spent and errors encountered
- Provides user-specific progress tracking

### Performance Reporting Service (Port: 8005)
Analyzes and generates performance metrics:
- Aggregates lab-specific performance data
- Tracks success rates and completion times
- Identifies common errors and challenges
- Generates detailed user performance reports

### Usage Analytics Service (Port: 8006)
Collects and analyzes platform-wide usage patterns:
- Tracks user engagement metrics
- Monitors resource utilization
- Provides trend analysis and insights
- Records various types of usage events

## Technology Stack
- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL Latest
- **Containerization**: Docker & Docker Compose
- **Network**: Custom virtual network for service communication

## Requirements
- Docker
- Docker Compose
- PostgreSQL Latest (currently 17.4)
- Python 3.11+

## Setup
1. Clone the repository:
```bash
git clone https://github.com/nh2seven/AR_1
cd AR_1
```

2. Start all services:
```bash
docker-compose up --build
```

## Service Endpoints
Once running, the services are available locally at:
- User Progress Service: http://localhost:8004
- Performance Reporting Service: http://localhost:8005
- Usage Analytics Service: http://localhost:8006

API documentation (Swagger UI) is available at `/docs` for each service:
- http://localhost:8004/docs
- http://localhost:8005/docs
- http://localhost:8006/docs

### Example API Requests

#### User Management (All Services)
All three services share similar user management endpoints. Here's how to create and retrieve users:

**Create a user:**
```bash
curl -X 'POST' 'http://localhost:8004/users/' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{
  "username": "testuser1",
  "full_name": "Test User",
  "email": "testuser1@example.com"
}'
```

**Response:**
```json
{
  "username": "testuser1",
  "full_name": "Test User",
  "email": "testuser1@example.com",
  "id": "7be06c80-fbc6-4280-aed1-16f8749df77b",
  "created_at": "2025-04-19T08:30:38.538812",
  "last_active": "2025-04-19T08:30:38.538812"
}
```

#### Lab Management (All Services)
Similarly, all services share lab management endpoints:

**Create a lab:**
```bash
curl -X 'POST' 'http://localhost:8004/labs/' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{
  "name": "Filesystem Lab",
  "description": "Learn about filesystem operations",
  "lab_type": "filesystem",
  "difficulty": "beginner"
}'
```

**Response:**
```json
{
  "name": "Filesystem Lab",
  "description": "Learn about filesystem operations",
  "lab_type": "filesystem",
  "difficulty": "beginner",
  "id": "e92c5db5-8d10-4bf7-b824-60a760481db9",
  "created_at": "2025-04-19T08:31:38.605877",
  "updated_at": "2025-04-19T08:31:38.605877"
}
```

#### Service-Specific Endpoints

**Record User Progress (User Progress Service):**
```bash
curl -X 'POST' 'http://localhost:8004/progress/lab-attempt' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{
  "user_id": "7be06c80-fbc6-4280-aed1-16f8749df77b",
  "lab_type": "filesystem",
  "completion_status": true,
  "time_spent": 300,
  "errors_encountered": ["permission_denied", "file_not_found"]
}'
```

**Record Performance Data (Performance Reporting Service):**
```bash
curl -X 'POST' 'http://localhost:8005/performance/record' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{
  "user_id": "dc1a707b-d1f6-4c99-b7c5-544a16afbd9d",
  "lab_id": "8ef4e328-ac26-4cff-ab80-acb1bcc7a4f1",
  "lab_type": "filesystem",
  "score": 85,
  "completion_time": 295,
  "errors_made": 3,
  "success": true
}'
```

**Track User Events (Usage Analytics Service):**
```bash
curl -X 'POST' 'http://localhost:8006/analytics/event' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{
  "user_id": "269b9e2e-e021-4316-8a59-9a79ff19d828",
  "lab_id": "1c142292-2f0f-4b40-b8e5-4c301ce18e8b", 
  "lab_type": "filesystem",
  "event_type": "start",
  "details": {"session_id": "test-session-1"}
}'
```

See each service's individual README for more detailed API documentation.

A debugging container for the shared Postgres database is also available in the form of the default Postgres CLI:
```sh
docker compose up -d

# Connect to user progress database
docker compose exec pgadmin psql -h db -U postgres -d user_progress_db

# Connect to performance reporting database
docker compose exec pgadmin psql -h db -U postgres -d performance_db

# Connect to usage analytics database
docker compose exec pgadmin psql -h db -U postgres -d usage_analytics_db
```

## Architecture
The platform uses a microservices architecture where:
- Each service has its own database and API
- Services communicate via REST APIs
- All services are connected through a shared Docker network
- Data persistence is handled via Docker volumes

## License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.