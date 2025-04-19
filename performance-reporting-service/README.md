# Performance Reporting Service
Analyzes and reports on lab performance metrics across users and lab types.

## Service Architecture
This service focuses solely on collecting, analyzing, and reporting performance metrics for labs and users. It communicates with the User Progress Service to validate users and labs rather than maintaining duplicate user and lab data.

**Key features:**
- Records lab performance data (completion time, success rate, resource usage)
- Provides aggregate lab performance metrics 
- Provides detailed user performance metrics across all labs

## API Endpoints
### Performance Endpoints
#### POST /performance/record
Record performance data for a lab attempt.

**Request:**
```json
{
  "user_id": "dc1a707b-d1f6-4c99-b7c5-544a16afbd9d",
  "lab_type": "filesystem",
  "completion_time": 295,
  "success": true,
  "errors": ["permission_denied"],
  "resources_used": {"memory": 128, "cpu": 25}
}
```

**Response:**
```json
{
  "user_id": "dc1a707b-d1f6-4c99-b7c5-544a16afbd9d",
  "lab_type": "filesystem",
  "completion_time": 295,
  "success": true,
  "errors": ["permission_denied"],
  "resources_used": {"memory": 128, "cpu": 25},
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
  "total_users": 1,
  "avg_completion_time": 295.0,
  "success_rate": 1.0,
  "common_errors": ["permission_denied"],
  "id": 1,
  "last_updated": "2025-04-19T11:16:47.606301Z"
}
```

#### GET /performance/user/{user_id}
Get detailed performance metrics for a specific user across all labs.

**Response:**
```json
{
  "user_id": "dc1a707b-d1f6-4c99-b7c5-544a16afbd9d",
  "performance_by_lab": {
    "filesystem": {
      "lab_type": "filesystem",
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
- Dependencies: 
  - PostgreSQL database
  - User Progress Service (for user and lab validation)

## Environment Variables
- `USER_PROGRESS_SERVICE_URL`: URL for the User Progress Service (default: http://user-progress:8000)

## Setup
```bash
docker-compose up --build
```

Access the API documentation at http://localhost:8005/docs