# Performance Reporting Service

Analyzes and reports on lab performance metrics across users and lab types.

## API Endpoints

### POST /performance/record
Record performance data for a lab attempt.

```json
{
  "user_id": "string",
  "lab_type": "string",
  "completion_time": 300,
  "success": true,
  "errors": ["error1", "error2"],
  "resources_used": {
    "memory": 1024,
    "cpu_time": 200
  }
}
```

### GET /performance/lab/{lab_type}
Get aggregated performance metrics for a specific lab type:
- Total users
- Average completion time
- Success rate
- Common errors

### GET /performance/user/{user_id}
Get detailed performance metrics for a specific user across all labs.

## Integration

- Port: 8005
- Network: virtual-labs-network
- Dependencies: None

## Setup

```bash
docker-compose up --build
```

Access the API documentation at http://localhost:8005/docs