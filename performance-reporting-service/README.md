# Performance Reporting Service

Analyzes and reports on lab performance metrics across users and lab types.

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
  "id": "dc1a707b-d1f6-4c99-b7c5-544a16afbd9d",
  "created_at": "2025-04-19T08:30:55.808428",
  "last_active": "2025-04-19T08:30:55.808430"
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
  "id": "8ef4e328-ac26-4cff-ab80-acb1bcc7a4f1",
  "created_at": "2025-04-19T08:32:04.317717",
  "updated_at": "2025-04-19T08:32:04.317720"
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

### Performance Endpoints

#### POST /performance/record
Record performance data for a lab attempt.

**Request:**
```json
{
  "user_id": "dc1a707b-d1f6-4c99-b7c5-544a16afbd9d",
  "lab_id": "8ef4e328-ac26-4cff-ab80-acb1bcc7a4f1",
  "lab_type": "filesystem",
  "score": 85,
  "completion_time": 295,
  "errors_made": 3,
  "success": true
}
```

**Response:**
```json
{
  "user_id": "dc1a707b-d1f6-4c99-b7c5-544a16afbd9d",
  "lab_type": "filesystem",
  "completion_time": 295,
  "success": true,
  "errors": [],
  "resources_used": {},
  "id": 2,
  "timestamp": "2025-04-19T08:38:25.379893Z"
}
```

#### GET /performance/lab/{lab_type}
Get aggregated performance metrics for a specific lab type.

**Response:**
```json
{
  "lab_type": "filesystem",
  "lab_name": "Filesystem Lab",
  "total_attempts": 1,
  "unique_users": 1,
  "success_rate": 1.0,
  "avg_completion_time": 295.0,
  "common_errors": []
}
```

#### GET /performance/user/{user_id}
Get detailed performance metrics for a specific user across all labs.

**Response:**
```json
{
  "user_id": "dc1a707b-d1f6-4c99-b7c5-544a16afbd9d",
  "username": "testuser1",
  "performance_by_lab": {
    "filesystem": {
      "lab_name": "Filesystem Lab",
      "lab_description": "Learn about filesystem operations",
      "lab_difficulty": "beginner",
      "attempts": 1,
      "success_rate": 1.0,
      "avg_completion_time": 295.0,
      "total_time_spent": 295,
      "last_attempt": "2025-04-19T08:38:25.379893+00:00"
    }
  }
}
```

#### PUT /performance/record/{performance_id}
Update an existing performance record.

#### DELETE /performance/record/{performance_id}
Delete a performance record.

## Integration

- Port: 8005
- Network: virtual-labs-network
- Dependencies: PostgreSQL database

## Setup

```bash
docker-compose up --build
```

Access the API documentation at http://localhost:8005/docs