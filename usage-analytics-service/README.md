# Usage Analytics Service

Collects and analyzes usage patterns and events across the virtual labs platform.

## API Endpoints

### User Management

#### POST /users/
Create a new user.

**Request:**
```json
{
  "username": "testuser1",
  "full_name": "Test User",
  "email": "testuser1@example.com"
}
```

**Response:**
```json
{
  "username": "testuser1",
  "full_name": "Test User",
  "email": "testuser1@example.com",
  "id": "269b9e2e-e021-4316-8a59-9a79ff19d828",
  "created_at": "2025-04-19T08:31:15.505369",
  "last_active": "2025-04-19T08:31:15.505372"
}
```

#### GET /users/
List all users (with pagination).

#### GET /users/{user_id}
Get details of a specific user.

#### PUT /users/{user_id}
Update user information.

#### DELETE /users/{user_id}
Delete a user account.

### Lab Management

#### POST /labs/
Create a new lab.

**Request:**
```json
{
  "name": "Filesystem Lab",
  "description": "Learn about filesystem operations",
  "lab_type": "filesystem",
  "difficulty": "beginner"
}
```

**Response:**
```json
{
  "name": "Filesystem Lab",
  "description": "Learn about filesystem operations",
  "lab_type": "filesystem",
  "difficulty": "beginner",
  "id": "1c142292-2f0f-4b40-b8e5-4c301ce18e8b",
  "created_at": "2025-04-19T08:32:22.623769",
  "updated_at": "2025-04-19T08:32:22.623772"
}
```

#### GET /labs/
List all labs (with pagination).

#### GET /labs/{lab_id}
Get details of a specific lab.

#### GET /labs/type/{lab_type}
Get all labs of a specific type.

#### PUT /labs/{lab_id}
Update lab information.

#### DELETE /labs/{lab_id}
Delete a lab.

### Analytics Endpoints

#### POST /analytics/event
Record a usage event.

**Request:**
```json
{
  "user_id": "269b9e2e-e021-4316-8a59-9a79ff19d828",
  "lab_id": "1c142292-2f0f-4b40-b8e5-4c301ce18e8b", 
  "lab_type": "filesystem",
  "event_type": "start",
  "details": {"session_id": "test-session-1"}
}
```

**Response:**
```json
{
  "user_id": "269b9e2e-e021-4316-8a59-9a79ff19d828",
  "lab_type": "filesystem",
  "event_type": "start",
  "event_data": {},
  "id": 3,
  "timestamp": "2025-04-19T08:39:43.599397Z"
}
```

**Example of recording a lab completion event:**
```json
{
  "user_id": "269b9e2e-e021-4316-8a59-9a79ff19d828",
  "lab_id": "1c142292-2f0f-4b40-b8e5-4c301ce18e8b", 
  "lab_type": "filesystem",
  "event_type": "complete",
  "details": {"session_id": "test-session-1", "time_spent": 320}
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
- Dependencies: PostgreSQL database

## Setup

```bash
docker-compose up --build
```

Access the API documentation at http://localhost:8006/docs