# User Progress Service
Tracks user progress and attempts in virtual lab exercises. This service serves as the "source of truth" for user and lab data within the platform.

## Service Architecture
This service maintains the core data about users and labs, and provides:
- User management endpoints for creating, updating, and deleting users
- Lab management endpoints for creating, updating, and deleting labs
- Progress tracking for monitoring user attempts and performance

**Note:** Other microservices (Performance Reporting Service and Usage Analytics Service) communicate with this service to validate users and labs, rather than maintaining their own duplicate user and lab data.

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
  "id": "7be06c80-fbc6-4280-aed1-16f8749df77b",
  "created_at": "2025-04-19T08:30:38.538812",
  "last_active": "2025-04-19T08:30:38.538812"
}
```

#### GET /users/
List all users (with pagination).

**Query Parameters:**
- `skip` (integer, default=0): Number of records to skip
- `limit` (integer, default=100): Maximum number of records to return

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
  "id": "e92c5db5-8d10-4bf7-b824-60a760481db9",
  "created_at": "2025-04-19T08:31:38.605877",
  "updated_at": "2025-04-19T08:31:38.605877"
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

### Progress Tracking
#### POST /progress/lab-attempt
Record a new lab attempt by a user.

**Request:**
```json
{
  "user_id": "7be06c80-fbc6-4280-aed1-16f8749df77b",
  "lab_type": "filesystem",
  "completion_status": true,
  "time_spent": 300,
  "errors_encountered": ["permission_denied", "file_not_found"]
}
```

**Response:**
```json
{
  "user_id": "7be06c80-fbc6-4280-aed1-16f8749df77b",
  "lab_type": "filesystem",
  "completion_status": true,
  "time_spent": 300,
  "errors_encountered": ["permission_denied", "file_not_found"],
  "id": 2,
  "timestamp": "2025-04-19T08:32:45.855898",
  "lab_name": "Filesystem Lab",
  "lab_description": "Learn about filesystem operations",
  "lab_difficulty": "beginner"
}
```

#### GET /progress/{user_id}
Get all lab attempts for a specific user.

**Response:**
```json
[
  {
    "user_id": "7be06c80-fbc6-4280-aed1-16f8749df77b",
    "lab_type": "filesystem",
    "completion_status": true,
    "time_spent": 300,
    "errors_encountered": ["permission_denied", "file_not_found"],
    "id": 2,
    "timestamp": "2025-04-19T08:32:45.855898",
    "lab_name": "Filesystem Lab",
    "lab_description": "Learn about filesystem operations",
    "lab_difficulty": "beginner"
  }
]
```

#### GET /progress/stats/{user_id}
Get aggregated statistics for a user.

**Response:**
```json
{
  "user_id": "7be06c80-fbc6-4280-aed1-16f8749df77b",
  "username": "testuser1",
  "total_attempts": 1,
  "successful_attempts": 1,
  "success_rate": 1.0,
  "average_time_per_attempt": 300.0,
  "labs_attempted": [
    {
      "lab_type": "filesystem",
      "lab_name": "Filesystem Lab",
      "attempts": 1,
      "successful_attempts": 1,
      "average_time": 300.0,
      "success_rate": 1.0
    }
  ]
}
```

## Integration
- Port: 8004
- Network: virtual-labs-network
- Dependencies: PostgreSQL database
- Services that depend on this:
  - Performance Reporting Service
  - Usage Analytics Service

## Setup
```bash
docker-compose up --build
```

Access the API documentation at http://localhost:8004/docs