# Infrastructure Integration Service

This service integrates our CC_Project microservices with the Infrastructure-Microservice system developed by another team. It enhances our analytics and reporting capabilities by incorporating infrastructure-level insights.

## Integration Description

The Integration Service serves as a bridge between:
- Our CC_Project microservices (User Progress, Performance Reporting, Usage Analytics)
- The Infrastructure-Microservice system (https://github.com/Kritin-Thakur/Infrastructure-Microservice)

This integration adds value by combining application-level analytics with infrastructure-level insights, enabling a comprehensive view of the virtual labs platform.

## ⚠️ Current Integration Status

**IMPORTANT:** The integration is currently using mock data because the Infrastructure-Microservice services are not properly accessible. This is because:

1. Their services require a MySQL database setup (as specified in their `sqlcode.txt`)
2. Their services are not containerized, making integration difficult
3. There's no accessible running instance of their services

### Requirements from Infrastructure-Microservice Team

For proper integration, the Infrastructure-Microservice team should:

1. **Containerize their services** - Provide Docker containers that include:
   - Their Node.js microservices
   - The required MySQL database with sample data
   - All necessary environment configuration

2. **OR provide a stable running environment** - Make their services available on a consistent host/port with proper database connectivity

Until one of these requirements is met, our integration will continue to use mock data that approximates the expected output from their services.

## Integrated Functionality

The service provides two main integration points:

### 1. Lab Utilization Analytics Integration
- Enhances our Usage Analytics with infrastructure-level lab utilization data
- Identifies popular labs based on sessions and user minutes
- Shows lab utilization status (over/under-utilized) based on actual vs. expected usage

### 2. Server Resource Allocation Integration
- Correlates our performance metrics with server allocation data
- Provides visibility into server resource usage for different labs
- Shows how labs are distributed across infrastructure

## API Endpoints

The Integration Service runs on port 8007 and exposes the following endpoints:

- `GET /` - Service information and available endpoints
- `GET /integration/lab-utilization` - Enhanced lab utilization analytics
- `GET /integration/lab-utilization/{lab_type}` - Lab utilization for a specific lab type
- `GET /integration/server-allocation` - Enhanced server allocation metrics
- `GET /integration/server-allocation/{lab_type}` - Server allocation for a specific lab type

## Example API Requests

**Get enhanced lab utilization analytics:**
```bash
curl http://localhost:8007/integration/lab-utilization
```

**Get enhanced server allocation metrics:**
```bash
curl http://localhost:8007/integration/server-allocation
```

**Get lab-specific utilization:**
```bash
curl http://localhost:8007/integration/lab-utilization/filesystem
```

## Implementation Details

The integration is implemented using adapter classes that:
1. Connect to our CC_Project services for application-level data
2. Connect to Infrastructure-Microservice services for infrastructure data
3. Combine the data to provide enhanced insights
4. Include fallback mock data for when Infrastructure-Microservice services are unavailable

## Requirements

- Docker and Docker Compose (for running the service in a container)
- Python 3.11+ with FastAPI, Uvicorn, and Requests (for local development)
- Network connectivity to both CC_Project services and Infrastructure-Microservice services

## Running the Service

The Integration Service is included in the main docker-compose.yml and starts alongside other CC_Project services:

```bash
cd /path/to/CC_Project
docker compose up -d
```

## Configuration

The service uses the following environment variables (already configured in docker-compose.yml):

- `INTEGRATION_API_PORT` - Port for the Integration API (default: 8007)
- `LAB_MONITORING_URL` - URL for the Lab Monitoring Service
- `RESOURCE_ALLOCATION_URL` - URL for the Resource Allocation Service
- `PERFORMANCE_SERVICE_URL` - URL for the Performance Service
- `USAGE_ANALYTICS_URL` - URL for our Usage Analytics Service
- `PERFORMANCE_REPORTING_URL` - URL for our Performance Reporting Service

## Notes

- The integration is designed to be resilient, with fallback mock data when external services are unavailable
- No modifications are required to the Infrastructure-Microservice codebase
- The service maps between our lab types and their lab IDs using a simple mapping strategy