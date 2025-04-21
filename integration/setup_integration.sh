#!/bin/bash
# Integration Setup Script
# This script sets up and tests the integration between CC_Project and Infrastructure-Microservice
# Date: April 21, 2025

set -e  # Exit on error
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

echo -e "${BLUE}===== CC_Project Integration Setup =====${NC}"
echo "Date: $(date)"
echo ""

# 1. Check if MySQL is running
echo -e "${BLUE}Checking MySQL...${NC}"
if command -v mysql &> /dev/null; then
    echo -e "${GREEN}✓ MySQL client found${NC}"
    
    # First try password-less connection
    if mysql --host=127.0.0.1 -u root -e "SELECT 1" 2>/dev/null || 
       mysql --socket=/tmp/mysql.sock -u root -e "SELECT 1" 2>/dev/null; then
        echo -e "${GREEN}✓ MySQL server is running${NC}"
        MYSQL_CMD="mysql -u root"
    else
        # Try with password if no-password connection fails
        echo -e "${YELLOW}MySQL server requires password authentication${NC}"
        echo -n "Enter MySQL root password: "
        read -s MYSQL_PASSWORD
        echo ""
        
        if mysql --host=127.0.0.1 -u root -p"$MYSQL_PASSWORD" -e "SELECT 1" 2>/dev/null; then
            echo -e "${GREEN}✓ MySQL server is running${NC}"
            MYSQL_CMD="mysql -u root -p$MYSQL_PASSWORD"
        else
            echo -e "${RED}✗ MySQL authentication failed${NC}"
            echo -e "${YELLOW}Please check your MySQL root password and try again${NC}"
            exit 1
        fi
    fi
else
    echo -e "${RED}✗ MySQL client not found${NC}"
    echo -e "${YELLOW}Please install MySQL client and run this script again${NC}"
    exit 1
fi

# 2. Set up the Infrastructure-Microservice database
echo -e "\n${BLUE}Setting up Infrastructure-Microservice database...${NC}"
if [ -n "$MYSQL_PASSWORD" ]; then
    # Use the password if it was provided
    mysql -u root -p"$MYSQL_PASSWORD" < setup_infra_db.sql && \
        echo -e "${GREEN}✓ Database setup complete${NC}" || \
        (echo -e "${RED}✗ Error setting up database${NC}" && exit 1)
else
    # Try without password
    mysql -u root < setup_infra_db.sql && \
        echo -e "${GREEN}✓ Database setup complete${NC}" || \
        (echo -e "${RED}✗ Error setting up database${NC}" && exit 1)
fi

# 3. Check if the required packages are installed
echo -e "\n${BLUE}Checking required Python packages...${NC}"
if ! command -v pip &> /dev/null; then
    echo -e "${RED}✗ pip not found${NC}"
    echo -e "${YELLOW}Please install pip and run this script again${NC}"
    exit 1
fi

echo "Installing required packages..."
pip install -r requirements.txt

# 4. Check if the Infrastructure-Microservice services are running
echo -e "\n${BLUE}Checking Infrastructure-Microservice services...${NC}"

# Function to check if a service is running
check_service() {
    local name=$1
    local url=$2
    
    echo -n "Checking $name... "
    if curl -s --head --fail "$url" &> /dev/null; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${YELLOW}✗ Not running${NC}"
        return 1
    fi
}

# These are the services we depend on
SERVICES_OK=true
check_service "Lab Monitoring Service" "http://localhost:3003/monitor/labs" || SERVICES_OK=false
check_service "Resource Allocation Service" "http://localhost:3005/servers" || SERVICES_OK=false
check_service "Performance Service" "http://localhost:3004/performance/servers/stats" || SERVICES_OK=false

if [ "$SERVICES_OK" = false ]; then
    echo -e "\n${YELLOW}Some Infrastructure-Microservice services are not running${NC}"
    echo -e "Would you like to start them? (y/n)"
    read -r START_SERVICES
    if [[ "$START_SERVICES" == "y" ]]; then
        echo "Starting services in separate terminals..."
        # Use different terminals or backgrounds
        cd "../../Infrastructure-Microservice/backend/lab-monitoring-service" && node server.js &
        cd "../../Infrastructure-Microservice/backend/resourceAllocation" && node server.js &
        cd "../../Infrastructure-Microservice/backend/performance-service" && node server.js &
        echo "Waiting for services to start..."
        sleep 5
    else
        echo -e "${YELLOW}Warning: Integration will use fallback mock data if services are not running${NC}"
    fi
fi

# 5. Start the integration service
echo -e "\n${BLUE}Starting the integration service...${NC}"
echo "You can run the service using:"
echo "python integration_api.py"

echo -e "\nYou can also build and run the Docker container with:"
echo "docker-compose up --build -d"

echo -e "\n${BLUE}===== Integration Setup Complete =====${NC}"
echo "You can test the integration with the test_integration.sh script"
echo ""