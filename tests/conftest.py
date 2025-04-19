import pytest
import httpx
import time
import os
import uuid

# Service URLs - with configurable overrides for local testing
USER_PROGRESS_URL = os.getenv("USER_PROGRESS_URL", "http://localhost:8004")
PERFORMANCE_REPORTING_URL = os.getenv("PERFORMANCE_REPORTING_URL", "http://localhost:8005")
USAGE_ANALYTICS_URL = os.getenv("USAGE_ANALYTICS_URL", "http://localhost:8006")

# Test data fixtures
@pytest.fixture
def test_user_data():
    """Create unique test user data for tests."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"testuser{unique_id}",
        "full_name": "Test User",
        "email": f"testuser{unique_id}@example.com"
    }

@pytest.fixture
def test_lab_data():
    """Create unique test lab data for tests."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"Test Lab {unique_id}",
        "description": "A test lab for automated testing",
        "lab_type": f"test-lab-{unique_id}",
        "difficulty": "beginner"
    }

@pytest.fixture
def created_test_user(test_user_data):
    """Create a test user and return its data including ID."""
    with httpx.Client() as client:
        try:
            response = client.post(f"{USER_PROGRESS_URL}/users/", json=test_user_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            pytest.skip(f"Failed to create test user: {str(e)}")

@pytest.fixture
def created_test_lab(test_lab_data):
    """Create a test lab and return its data including ID."""
    with httpx.Client() as client:
        try:
            response = client.post(f"{USER_PROGRESS_URL}/labs/", json=test_lab_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            pytest.skip(f"Failed to create test lab: {str(e)}")

@pytest.fixture
def wait_for_services():
    """Wait for all services to be available."""
    services = [
        (USER_PROGRESS_URL, "User Progress"),
        (PERFORMANCE_REPORTING_URL, "Performance Reporting"),
        (USAGE_ANALYTICS_URL, "Usage Analytics")
    ]
    
    max_retries = 5
    retry_interval = 2
    
    for url, name in services:
        for attempt in range(max_retries):
            try:
                response = httpx.get(f"{url}/docs")
                if response.status_code < 500:  # Accept any non-server error
                    break
            except httpx.HTTPError:
                pass
            
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
                print(f"Waiting for {name} service to be available...")
            else:
                pytest.skip(f"{name} service is not available after {max_retries} attempts")

# HTTP client fixtures
@pytest.fixture
def http_client():
    """Create a reusable HTTP client."""
    with httpx.Client() as client:
        yield client

@pytest.fixture
def async_http_client():
    """Create a reusable async HTTP client."""
    client = httpx.AsyncClient()
    yield client
    # Close the async client explicitly
    import asyncio
    asyncio.run(client.aclose())