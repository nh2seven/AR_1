import pytest
import httpx
import os
from http import HTTPStatus

# Service URL
USER_PROGRESS_URL = os.getenv("USER_PROGRESS_URL", "http://localhost:8004")

class TestUserProgressService:
    """Tests for the User Progress Service endpoints."""
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_create_and_get_user(self, test_user_data, http_client):
        """Test creating and retrieving a user."""
        # Create user
        create_response = http_client.post(f"{USER_PROGRESS_URL}/users/", json=test_user_data)
        assert create_response.status_code == HTTPStatus.OK, f"Failed to create user: {create_response.text}"
        
        user_data = create_response.json()
        assert "id" in user_data, "User ID not returned in response"
        assert user_data["username"] == test_user_data["username"]
        
        # Get user by ID
        user_id = user_data["id"]
        get_response = http_client.get(f"{USER_PROGRESS_URL}/users/{user_id}")
        assert get_response.status_code == HTTPStatus.OK, f"Failed to get user: {get_response.text}"
        
        retrieved_user = get_response.json()
        assert retrieved_user["id"] == user_id
        assert retrieved_user["username"] == test_user_data["username"]
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_list_users(self, created_test_user, http_client):
        """Test listing all users."""
        response = http_client.get(f"{USER_PROGRESS_URL}/users/")
        assert response.status_code == HTTPStatus.OK, f"Failed to list users: {response.text}"
        
        users = response.json()
        assert isinstance(users, list), "Response is not a list"
        # Check if our test user is in the list
        assert any(user["id"] == created_test_user["id"] for user in users), "Created test user not found in list"
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_update_user(self, created_test_user, http_client):
        """Test updating a user."""
        user_id = created_test_user["id"]
        update_data = {
            "username": created_test_user["username"],
            "full_name": "Updated Test User",
            "email": created_test_user["email"]
        }
        
        response = http_client.put(f"{USER_PROGRESS_URL}/users/{user_id}", json=update_data)
        assert response.status_code == HTTPStatus.OK, f"Failed to update user: {response.text}"
        
        updated_user = response.json()
        assert updated_user["full_name"] == "Updated Test User"
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_create_and_get_lab(self, test_lab_data, http_client):
        """Test creating and retrieving a lab."""
        # Create lab
        create_response = http_client.post(f"{USER_PROGRESS_URL}/labs/", json=test_lab_data)
        assert create_response.status_code == HTTPStatus.OK, f"Failed to create lab: {create_response.text}"
        
        lab_data = create_response.json()
        assert "id" in lab_data, "Lab ID not returned in response"
        assert lab_data["name"] == test_lab_data["name"]
        
        # Get lab by ID
        lab_id = lab_data["id"]
        get_response = http_client.get(f"{USER_PROGRESS_URL}/labs/{lab_id}")
        assert get_response.status_code == HTTPStatus.OK, f"Failed to get lab: {get_response.text}"
        
        retrieved_lab = get_response.json()
        assert retrieved_lab["id"] == lab_id
        assert retrieved_lab["name"] == test_lab_data["name"]
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_list_labs(self, created_test_lab, http_client):
        """Test listing all labs."""
        response = http_client.get(f"{USER_PROGRESS_URL}/labs/")
        assert response.status_code == HTTPStatus.OK, f"Failed to list labs: {response.text}"
        
        labs = response.json()
        assert isinstance(labs, list), "Response is not a list"
        # Check if our test lab is in the list
        assert any(lab["id"] == created_test_lab["id"] for lab in labs), "Created test lab not found in list"
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_get_labs_by_type(self, created_test_lab, http_client):
        """Test getting labs by type."""
        lab_type = created_test_lab["lab_type"]
        response = http_client.get(f"{USER_PROGRESS_URL}/labs/type/{lab_type}")
        assert response.status_code == HTTPStatus.OK, f"Failed to get labs by type: {response.text}"
        
        labs = response.json()
        assert isinstance(labs, list), "Response is not a list"
        assert len(labs) > 0, "No labs returned"
        assert labs[0]["lab_type"] == lab_type
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_record_lab_attempt(self, created_test_user, created_test_lab, http_client):
        """Test recording a lab attempt."""
        attempt_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "completion_status": True,
            "time_spent": 300,
            "errors_encountered": ["permission_denied", "file_not_found"]
        }
        
        response = http_client.post(f"{USER_PROGRESS_URL}/progress/lab-attempt", json=attempt_data)
        assert response.status_code == HTTPStatus.OK, f"Failed to record lab attempt: {response.text}"
        
        attempt = response.json()
        assert attempt["user_id"] == created_test_user["id"]
        assert attempt["lab_type"] == created_test_lab["lab_type"]
        assert attempt["completion_status"] == True
        assert attempt["time_spent"] == 300
        assert "id" in attempt, "Attempt ID not returned in response"
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_get_user_progress(self, created_test_user, created_test_lab, http_client):
        """Test getting user progress."""
        # First create an attempt for the user
        attempt_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "completion_status": True,
            "time_spent": 300,
            "errors_encountered": ["permission_denied"]
        }
        
        http_client.post(f"{USER_PROGRESS_URL}/progress/lab-attempt", json=attempt_data)
        
        # Get progress for the user
        response = http_client.get(f"{USER_PROGRESS_URL}/progress/{created_test_user['id']}")
        assert response.status_code == HTTPStatus.OK, f"Failed to get user progress: {response.text}"
        
        progress = response.json()
        assert isinstance(progress, list), "Response is not a list"
        assert len(progress) > 0, "No progress records found"
        assert progress[0]["user_id"] == created_test_user["id"]
        assert progress[0]["lab_type"] == created_test_lab["lab_type"]
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_get_user_stats(self, created_test_user, created_test_lab, http_client):
        """Test getting user statistics."""
        # First create an attempt for the user
        attempt_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "completion_status": True,
            "time_spent": 300,
            "errors_encountered": ["permission_denied"]
        }
        
        http_client.post(f"{USER_PROGRESS_URL}/progress/lab-attempt", json=attempt_data)
        
        # Get statistics for the user
        response = http_client.get(f"{USER_PROGRESS_URL}/progress/stats/{created_test_user['id']}")
        assert response.status_code == HTTPStatus.OK, f"Failed to get user stats: {response.text}"
        
        stats = response.json()
        assert stats["user_id"] == created_test_user["id"]
        assert "total_attempts" in stats
        assert stats["total_attempts"] > 0
        assert "success_rate" in stats
        assert "labs_attempted" in stats
        assert len(stats["labs_attempted"]) > 0