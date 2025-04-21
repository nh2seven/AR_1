#!/bin/bash

# Test script for Integration Service with Infrastructure-Microservice
# This script checks the status of all required services and tests the integration endpoints
# Updated: April 20, 2025 - Removed mock data references and enhanced output display

echo "===== Infrastructure Integration Test ====="
echo "Date: $(date)"
echo ""

# Define service URLs
INTEGRATION_URL="http://localhost:8007"
USER_PROGRESS_URL="http://localhost:8004"
PERFORMANCE_REPORTING_URL="http://localhost:8005"
USAGE_ANALYTICS_URL="http://localhost:8006"

LAB_MONITORING_URL="http://localhost:3003"
RESOURCE_ALLOCATION_URL="http://localhost:3005"
PERFORMANCE_SERVICE_URL="http://localhost:3004"

# Function to format JSON for better readability
format_json() {
    echo "$1" | python -m json.tool | sed 's/^/    /'
}

# Check if our own services are running
echo "Checking CC_Project microservices..."

if curl -s -f "${USER_PROGRESS_URL}" > /dev/null; then
    echo "User Progress Service is running"
else
    echo "X User Progress Service is not running at ${USER_PROGRESS_URL}"
    echo "   Start it with: cd ../user-progress-service && python -m app.main"
fi

if curl -s -f "${PERFORMANCE_REPORTING_URL}" > /dev/null; then
    echo "Performance Reporting Service is running"
else
    echo "X Performance Reporting Service is not running at ${PERFORMANCE_REPORTING_URL}"
    echo "   Start it with: cd ../performance-reporting-service && python -m app.main"
fi

if curl -s -f "${USAGE_ANALYTICS_URL}" > /dev/null; then
    echo "Usage Analytics Service is running"
else
    echo "X Usage Analytics Service is not running at ${USAGE_ANALYTICS_URL}"
    echo "   Start it with: cd ../usage-analytics-service && python -m app.main"
fi

# Check if Integration Service is running
if curl -s -f "${INTEGRATION_URL}" > /dev/null; then
    echo "Integration Service is running"
else
    echo "X Integration Service is not running"
    echo "   Starting Integration Service..."
    # Use environment variables to explicitly set URLs for testing
    export LAB_MONITORING_URL="${LAB_MONITORING_URL}"
    export RESOURCE_ALLOCATION_URL="${RESOURCE_ALLOCATION_URL}"
    export PERFORMANCE_SERVICE_URL="${PERFORMANCE_SERVICE_URL}"
    export USAGE_ANALYTICS_URL="${USAGE_ANALYTICS_URL}"
    export PERFORMANCE_REPORTING_URL="${PERFORMANCE_REPORTING_URL}"
    
    # Start the integration service in the background
    cd "$(dirname "$0")" && python integration_api.py &
    INTEGRATION_PID=$!
    echo "   Integration Service started with PID: ${INTEGRATION_PID}"
    echo "   Waiting for service to initialize..."
    sleep 3
fi

# Check if external services are running
echo ""
echo "Checking Infrastructure-Microservice services..."

if curl -s -f "${LAB_MONITORING_URL}/monitor/labs/popular" > /dev/null; then
    echo "Lab Monitoring Service is running"
else
    echo "X Lab Monitoring Service is not running at ${LAB_MONITORING_URL}"
    echo "   Start it with: cd ../../Others/Infrastructure-Microservice/backend/lab-monitoring-service && node server.js"
    echo "   WARNING: Integration will fail without this service"
fi

if curl -s -f "${RESOURCE_ALLOCATION_URL}/servers" > /dev/null; then
    echo "Resource Allocation Service is running"
else
    echo "X Resource Allocation Service is not running at ${RESOURCE_ALLOCATION_URL}"
    echo "   Start it with: cd ../../Others/Infrastructure-Microservice/backend/resourceAllocation && node server.js"
    echo "   WARNING: Integration will fail without this service"
fi

if curl -s -f "${PERFORMANCE_SERVICE_URL}/performance/servers/stats" > /dev/null; then
    echo "Performance Service is running"
else
    echo "X Performance Service is not running at ${PERFORMANCE_SERVICE_URL}"
    echo "   Start it with: cd ../../Others/Infrastructure-Microservice/backend/performance-service && node server.js"
    echo "   WARNING: Integration will fail without this service"
fi

# Test the integration endpoints
echo ""
echo "Testing Integration Service endpoints..."

# Test lab utilization endpoint
echo -e "\n===== Lab Utilization Integration ====="
echo "Endpoint: GET ${INTEGRATION_URL}/integration/lab-utilization"
LAB_UTIL_RESULT=$(curl -s -f "${INTEGRATION_URL}/integration/lab-utilization")

if [ $? -eq 0 ]; then
    # Count the number of labs in the response
    LAB_COUNT=$(echo "${LAB_UTIL_RESULT}" | grep -o "lab_type" | wc -l)
    echo "Lab utilization integration successful (${LAB_COUNT} labs found)"
    echo -e "\nResponse Summary:"
    TIMESTAMP=$(echo "${LAB_UTIL_RESULT}" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('timestamp', 'N/A'))")
    LAB_USAGE_COUNT=$(echo "${LAB_UTIL_RESULT}" | python -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('lab_usage', {})))")
    POPULAR_LABS=$(echo "${LAB_UTIL_RESULT}" | python -c "import sys, json; data=json.load(sys.stdin); labs = data.get('infrastructure_insights', {}).get('popular_labs', []); print(', '.join([lab.get('name', 'Unknown') for lab in labs]))")
    echo "  Timestamp: ${TIMESTAMP}"
    echo "  Labs with usage data: ${LAB_USAGE_COUNT}"
    echo "  Popular labs: ${POPULAR_LABS}"
    
    echo -e "\nFull Response:"
    format_json "${LAB_UTIL_RESULT}"
else
    echo "X Lab utilization integration failed"
fi

# Test server allocation endpoint
echo -e "\n===== Server Allocation Integration ====="
echo "Endpoint: GET ${INTEGRATION_URL}/integration/server-allocation"
SERVER_ALLOC_RESULT=$(curl -s -f "${INTEGRATION_URL}/integration/server-allocation")

if [ $? -eq 0 ]; then
    # Get information about servers in the response
    SERVER_COUNT=$(echo "${SERVER_ALLOC_RESULT}" | python -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('infrastructure', {}).get('servers', {})))")
    echo "Server allocation integration successful (${SERVER_COUNT} servers found)"
    
    echo -e "\nResponse Summary:"
    TIMESTAMP=$(echo "${SERVER_ALLOC_RESULT}" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('timestamp', 'N/A'))")
    ALLOCATION_COUNT=$(echo "${SERVER_ALLOC_RESULT}" | python -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('infrastructure', {}).get('allocation_map', {})))")
    SERVER_NAMES=$(echo "${SERVER_ALLOC_RESULT}" | python -c "import sys, json; data=json.load(sys.stdin); servers = data.get('infrastructure', {}).get('servers', {}); print(', '.join([info.get('name', f'Server-{id}') for id, info in servers.items()]))")
    
    echo "  Timestamp: ${TIMESTAMP}"
    echo "  Server count: ${SERVER_COUNT}"
    echo "  Lab allocations: ${ALLOCATION_COUNT}"
    echo "  Server names: ${SERVER_NAMES}"
    
    echo -e "\nFull Response:"
    format_json "${SERVER_ALLOC_RESULT}"
else
    echo "X Server allocation integration failed"
fi

# Find a valid lab type from the response
LAB_TYPE=$(echo "${SERVER_ALLOC_RESULT}" | python -c "import sys, json; data=json.load(sys.stdin); mapping = data.get('infrastructure', {}).get('allocation_map', {}); print(next(iter(mapping.keys()), 'linux-basics'))" 2>/dev/null || echo "linux-basics")

# Test specific lab type endpoint
echo -e "\n===== Lab-Specific Integration ====="
echo "Endpoint: GET ${INTEGRATION_URL}/integration/lab-utilization/${LAB_TYPE}"
LAB_SPECIFIC_RESULT=$(curl -s -f "${INTEGRATION_URL}/integration/lab-utilization/${LAB_TYPE}")

if [ $? -eq 0 ]; then
    # Parse the JSON response
    if python -c "import json, sys; json.loads(sys.stdin.read())" <<< "${LAB_SPECIFIC_RESULT}" >/dev/null 2>&1; then
        echo "Lab-specific integration successful for ${LAB_TYPE}"
        echo -e "\nFull Response:"
        format_json "${LAB_SPECIFIC_RESULT}"
    else
        echo "X Lab-specific integration failed: Invalid JSON response"
        echo "${LAB_SPECIFIC_RESULT}"
    fi
else
    echo "X Lab-specific integration failed for ${LAB_TYPE}"
fi

echo ""
echo "===== Integration Test Complete ====="
echo "All tests performed with live data from infrastructure services."

# If we started the integration service, ask if user wants to keep it running
if [ -n "${INTEGRATION_PID}" ]; then
    echo ""
    read -p "Keep Integration Service running? (y/n): " KEEP_RUNNING
    if [[ "${KEEP_RUNNING}" != "y" ]]; then
        echo "Stopping Integration Service (PID: ${INTEGRATION_PID})..."
        kill ${INTEGRATION_PID}
        echo "Integration Service stopped."
    else
        echo "Integration Service will continue running in the background (PID: ${INTEGRATION_PID})."
        echo "To stop it later, run: kill ${INTEGRATION_PID}"
    fi
fi
