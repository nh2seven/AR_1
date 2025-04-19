import pytest
import httpx
import os
from http import HTTPStatus

# Service URLs
USER_PROGRESS_URL = os.getenv("USER_PROGRESS_URL", "http://localhost:8004")
PERFORMANCE_REPORTING_URL = os.getenv("PERFORMANCE_REPORTING_URL", "http://localhost:8005")

class TestPerformanceReportingService:
    """Tests for the Performance Reporting Service endpoints."""
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_record_performance(self, created_test_user, created_test_lab, http_client):
        """Test recording performance data."""
        performance_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "completion_time": 290,
            "success": True,
            "errors": ["permission_denied"],
            "resources_used": {"memory": 128, "cpu": 25}
        }
        
        response = http_client.post(f"{PERFORMANCE_REPORTING_URL}/performance/record", json=performance_data)
        assert response.status_code == HTTPStatus.OK, f"Failed to record performance: {response.text}"
        
        record = response.json()
        assert record["user_id"] == created_test_user["id"]
        assert record["lab_type"] == created_test_lab["lab_type"]
        assert record["completion_time"] == 290
        assert record["success"] == True
        assert "id" in record, "Record ID not returned in response"
        assert "timestamp" in record, "Timestamp not returned in response"
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_get_lab_performance(self, created_test_user, created_test_lab, http_client):
        """Test getting lab performance metrics."""
        # First create a performance record
        performance_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "completion_time": 295,
            "success": True,
            "errors": ["file_not_found"],
            "resources_used": {"memory": 256, "cpu": 30}
        }
        
        http_client.post(f"{PERFORMANCE_REPORTING_URL}/performance/record", json=performance_data)
        
        # Get lab performance
        response = http_client.get(f"{PERFORMANCE_REPORTING_URL}/performance/lab/{created_test_lab['lab_type']}")
        assert response.status_code == HTTPStatus.OK, f"Failed to get lab performance: {response.text}"
        
        performance = response.json()
        assert performance["lab_type"] == created_test_lab["lab_type"]
        assert "total_users" in performance
        assert performance["total_users"] > 0
        assert "avg_completion_time" in performance
        assert "success_rate" in performance
        assert "common_errors" in performance
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_get_user_performance(self, created_test_user, created_test_lab, http_client):
        """Test getting user performance metrics."""
        # First create a performance record
        performance_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "completion_time": 300,
            "success": True,
            "errors": ["syntax_error"],
            "resources_used": {"memory": 128, "cpu": 20}
        }
        
        http_client.post(f"{PERFORMANCE_REPORTING_URL}/performance/record", json=performance_data)
        
        # Get user performance
        response = http_client.get(f"{PERFORMANCE_REPORTING_URL}/performance/user/{created_test_user['id']}")
        assert response.status_code == HTTPStatus.OK, f"Failed to get user performance: {response.text}"
        
        performance = response.json()
        assert performance["user_id"] == created_test_user["id"]
        assert "performance_by_lab" in performance
        assert created_test_lab["lab_type"] in performance["performance_by_lab"]
        lab_perf = performance["performance_by_lab"][created_test_lab["lab_type"]]
        assert "attempts" in lab_perf
        assert lab_perf["attempts"] > 0
        assert "success_rate" in lab_perf
        assert "avg_completion_time" in lab_perf
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_update_performance_record(self, created_test_user, created_test_lab, http_client):
        """Test updating a performance record."""
        # First create a performance record
        original_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "completion_time": 300,
            "success": False,
            "errors": ["syntax_error"],
            "resources_used": {"memory": 128, "cpu": 20}
        }
        
        create_response = http_client.post(f"{PERFORMANCE_REPORTING_URL}/performance/record", json=original_data)
        record = create_response.json()
        record_id = record["id"]
        
        # Update the record
        update_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "completion_time": 250,  # Changed value
            "success": True,  # Changed value
            "errors": ["syntax_error"],
            "resources_used": {"memory": 128, "cpu": 20}
        }
        
        response = http_client.put(f"{PERFORMANCE_REPORTING_URL}/performance/record/{record_id}", json=update_data)
        assert response.status_code == HTTPStatus.OK, f"Failed to update performance record: {response.text}"
        
        updated_record = response.json()
        assert updated_record["id"] == record_id
        assert updated_record["completion_time"] == 250
        assert updated_record["success"] == True
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_delete_performance_record(self, created_test_user, created_test_lab, http_client):
        """Test deleting a performance record."""
        # First create a performance record
        data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "completion_time": 300,
            "success": True,
            "errors": ["syntax_error"],
            "resources_used": {"memory": 128, "cpu": 20}
        }
        
        create_response = http_client.post(f"{PERFORMANCE_REPORTING_URL}/performance/record", json=data)
        record = create_response.json()
        record_id = record["id"]
        
        # Delete the record
        response = http_client.delete(f"{PERFORMANCE_REPORTING_URL}/performance/record/{record_id}")
        assert response.status_code == HTTPStatus.OK, f"Failed to delete performance record: {response.text}"
        
        # Verify deletion
        result = response.json()
        assert result["status"] == "success"
        assert f"Performance record {record_id} deleted" in result["message"]