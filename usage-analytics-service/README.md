# Usage Analytics Service
Collects and analyzes usage patterns and events across the virtual labs platform.

## Service Architecture
This service focuses solely on collecting and analyzing usage events and patterns. It communicates with the User Progress Service to validate users and labs rather than maintaining duplicate user and lab data.

**Key features:**
- Records various user interaction events (start, complete, error, etc.)
- Provides usage analytics for specific lab types
- Offers platform-wide usage trends and statistics

## API Endpoints
### Analytics Endpoints
#### POST /analytics/event
Record a usage event.

**Request:**
```json
{
  "user_id": "269b9e2e-e021-4316-8a59-9a79ff19d828",
  "lab_type": "filesystem",
  "event_type": "start",
  "event_data": {"session_id": "test-session-1"}
}
```

**Response:**
```json
{
  "user_id": "269b9e2e-e021-4316-8a59-9a79ff19d828",
  "lab_type": "filesystem",
  "event_type": "start",
  "event_data": {"session_id": "test-session-1"},
  "id": 3,
  "timestamp": "2025-04-19T08:39:43.599397Z"
}
```

**Example of recording a lab completion event:**
```json
{
  "user_id": "269b9e2e-e021-4316-8a59-9a79ff19d828",
  "lab_type": "filesystem",
  "event_type": "complete",
  "event_data": {"session_id": "test-session-1", "time_spent": 320}
}
```

#### GET /analytics/usage/lab/{lab_type}
Get usage analytics for a specific lab type over a time period.

**Query Parameters:**
- `days` (integer, default=7): Number of days to analyze

**Response:**
```json
{
  "lab_type": "filesystem",
  "time_period_days": 7,
  "unique_users": 1,
  "total_events": 2,
  "event_distribution": {
    "start": 1,
    "complete": 1
  },
  "average_session_time_seconds": 17.132421
}
```

#### GET /analytics/trends
Get platform-wide usage trends.

**Query Parameters:**
- `days` (integer, default=30): Number of days to analyze

**Response:**
```json
{
  "time_period_days": 30,
  "total_events": 2,
  "lab_usage": {
    "filesystem": {
      "total_events": 2,
      "unique_users": 1,
      "errors": 0
    }
  }
}
```

#### PUT /analytics/event/{event_id}
Update an existing event.

#### DELETE /analytics/event/{event_id}
Delete an event.

## Integration
- Port: 8006
- Network: virtual-labs-network
- Dependencies: 
  - PostgreSQL database
  - User Progress Service (for user and lab validation)

## Environment Variables
- `USER_PROGRESS_SERVICE_URL`: URL for the User Progress Service (default: http://user-progress:8000)

## Setup
```bash
docker-compose up --build
```

Access the API documentation at http://localhost:8006/docs