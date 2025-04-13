# User Progress Service

Tracks user progress and attempts in virtual lab exercises.

## API Endpoints

### POST /progress/lab-attempt
Record a new lab attempt by a user.

```json
{
  "user_id": "string",
  "lab_type": "string",
  "completion_status": true,
  "time_spent": 300,
  "errors_encountered": ["error1", "error2"]
}
```

### GET /progress/{user_id}
Get all lab attempts for a specific user.

### GET /progress/stats/{user_id}
Get aggregated statistics for a user including:
- Total attempts
- Success rate
- Average completion time

## Integration

- Port: 8004
- Network: virtual-labs-network
- Dependencies: None

## Setup

```bash
docker-compose up --build
```

Access the API documentation at http://localhost:8004/docs