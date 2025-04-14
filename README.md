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
- **Database**: PostgreSQL 15
- **Containerization**: Docker & Docker Compose
- **Network**: Custom virtual network for service communication

## Requirements
- Docker
- Docker Compose
- PostgreSQL 15
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

## Service URLs
Once running, the services are available locally at:
- User Progress Service: http://localhost:8004
- Performance Reporting Service: http://localhost:8005
- Usage Analytics Service: http://localhost:8006

API documentation (Swagger UI) is available at `/docs` for each service:
- http://localhost:8004/docs
- http://localhost:8005/docs
- http://localhost:8006/docs

## Architecture
The platform uses a microservices architecture where:
- Each service has its own database and API
- Services communicate via REST APIs
- All services are connected through a shared Docker network
- Data persistence is handled via Docker volumes

## License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.