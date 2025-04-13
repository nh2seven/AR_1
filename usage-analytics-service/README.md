# Usage Analytics Service

Collects and analyzes usage patterns and events across the virtual labs platform.

## API Endpoints

### POST /analytics/event
Record a usage event.

```json
{
  "user_id": "string",
  "lab_type": "string",
  "event_type": "start|complete|error|resource_access",
  "event_data": {
    "resource_type": "string",
    "action": "string",
    "details": {}
  }
}
```

### GET /analytics/usage/lab/{lab_type}
Get usage analytics for a specific lab type over a time period:
- Unique users
- Total events
- Event distribution
- Average session time

### GET /analytics/trends
Get platform-wide usage trends:
- Most used labs
- Error patterns
- User engagement metrics

## Integration

- Port: 8006
- Network: virtual-labs-network
- Dependencies: None

## Setup

```bash
docker-compose up --build
```

Access the API documentation at http://localhost:8006/docs