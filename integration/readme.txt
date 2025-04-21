# Infrastructure Integration Service - Microservices Integration Details
Date: April 21, 2025

## Overview
This document provides detailed information about the microservices integration implemented between our Analytics & Reporting (AR_1) platform and the Infrastructure-Microservice system. The Integration Service acts as a bridge that connects our application-level analytics services with infrastructure-level management services to provide enhanced insights.

## Integrated Microservices

### 1. Our AR_1 Microservices
- **User Progress Service** (Port: 8004)
  - Source of truth for user and lab data
  - Provides API endpoints for user management and lab progress tracking
  - Connection endpoint: http://localhost:8004

- **Performance Reporting Service** (Port: 8005)
  - Collects and analyzes performance metrics
  - Provides API endpoints for lab performance analytics
  - Connection endpoint: http://localhost:8005

- **Usage Analytics Service** (Port: 8006)
  - Tracks usage patterns and events
  - Provides API endpoints for usage statistics and trends
  - Connection endpoint: http://localhost:8006

### 2. External Infrastructure-Microservice Services
- **Lab Monitoring Service** (Port: 3003)
  - Monitors lab utilization and popularity
  - Provides endpoints for lab usage statistics
  - Connection endpoint: http://localhost:3003

- **Resource Allocation Service** (Port: 3005)
  - Manages server resources and allocation
  - Provides endpoints for server information and lab allocations
  - Connection endpoint: http://localhost:3005

- **Performance Service** (Port: 3004)
  - Collects server performance metrics
  - Provides endpoints for server statistics
  - Connection endpoint: http://localhost:3004

## Integration Implementation

### 1. Lab Utilization Adapter (`lab_utilization_adapter.py`)
This adapter enhances our Usage Analytics data with infrastructure-level lab utilization metrics:

- **Integration Points**:
  - Connects to Lab Monitoring Service (`/monitor/labs/popular`, `/monitor/labs/over-under-utilized`)
  - Connects to Usage Analytics Service (`/analytics/trends`, `/analytics/usage/lab/{lab_type}`)

- **Enhanced Data Provided**:
  - Popular labs based on sessions and user minutes
  - Lab utilization status (over/under-utilized)
  - Correlation between our application usage data and infrastructure utilization

### 2. Server Allocation Adapter (`server_allocation_adapter.py`)
This adapter correlates our performance data with server allocation information:

- **Integration Points**:
  - Connects to Resource Allocation Service (`/servers`, `/allocations`)
  - Connects to Performance Service (`/performance/servers/stats`, `/performance/servers/{id}/peaks`)
  - Connects to Performance Reporting Service (`/performance/lab/{lab_type}`, `/performance/user/{user_id}`)

- **Enhanced Data Provided**:
  - Server resource allocation by lab type
  - Performance metrics correlated with server infrastructure
  - Resource utilization insights

## Integration API Endpoints
The Integration Service exposes the following endpoints:

- `GET /integration/lab-utilization`
  - Combines usage analytics data with lab monitoring data
  - Returns enhanced lab utilization analytics

- `GET /integration/lab-utilization/{lab_type}`
  - Provides lab-specific utilization data
  - Filters the enhanced analytics for a specific lab type

- `GET /integration/server-allocation`
  - Combines performance metrics with server allocation data
  - Returns enhanced server allocation metrics

- `GET /integration/server-allocation/{lab_type}`
  - Provides lab-specific server allocation data
  - Filters the enhanced metrics for a specific lab type

## Integration Architecture
The integration follows an adapter pattern:
1. Each external service has a dedicated adapter class
2. Adapters handle connection, data transformation, and error handling
3. The Integration API exposes unified endpoints that combine data from multiple sources
4. Caching mechanisms ensure efficient operation and resilience

## Data Flow
1. Integration API receives a request
2. Appropriate adapter is activated based on request type
3. Adapter fetches data from our services and external services
4. Adapter combines and transforms the data
5. Enhanced data is returned to the client

## Error Handling and Resilience
- Connection retries (configured for 2 retries with 1-second delay)
- Response caching (5-minute cache duration)
- Graceful fallbacks when services are unavailable
- Comprehensive logging of integration events

## Integration Testing
Use the provided test script to verify integration status:
```
bash test_integration.sh
```

The script checks:
1. Status of all required services
2. Lab utilization integration
3. Server allocation integration
4. Lab-specific integrations

## Environment Configuration
The integration service uses the following environment variables:
- `LAB_MONITORING_URL` - URL for the Lab Monitoring Service
- `RESOURCE_ALLOCATION_URL` - URL for the Resource Allocation Service
- `PERFORMANCE_SERVICE_URL` - URL for the Performance Service
- `USAGE_ANALYTICS_URL` - URL for our Usage Analytics Service
- `PERFORMANCE_REPORTING_URL` - URL for our Performance Reporting Service
- `INTEGRATION_API_PORT` - Port for the Integration API (default: 8007)

## Project References
- Our AR_1 project: Analytics & Reporting platform
- Infrastructure-Microservice: https://github.com/Kritin-Thakur/Infrastructure-Microservice