import pytest
import httpx
import os
import time
from http import HTTPStatus

# Service URLs
USER_PROGRESS_URL = os.getenv("USER_PROGRESS_URL", "http://localhost:8004")
PERFORMANCE_REPORTING_URL = os.getenv("PERFORMANCE_REPORTING_URL", "http://localhost:8005")
USAGE_ANALYTICS_URL = os.getenv("USAGE_ANALYTICS_URL", "http://localhost:8006")

class TestCrossServiceIntegration:
    """Integration tests across multiple services."""
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_full_lab_workflow(self, test_user_data, test_lab_data, http_client):
        """Test a complete workflow across all services: create user and lab, record attempts,
        performance and usage data, then verify data is correctly reported in all services."""
        
        # Step 1: Create user in User Progress Service
        create_user_response = http_client.post(f"{USER_PROGRESS_URL}/users/", json=test_user_data)
        assert create_user_response.status_code == HTTPStatus.OK
        user = create_user_response.json()
        user_id = user["id"]
        
        # Step 2: Create lab in User Progress Service
        create_lab_response = http_client.post(f"{USER_PROGRESS_URL}/labs/", json=test_lab_data)
        assert create_lab_response.status_code == HTTPStatus.OK
        lab = create_lab_response.json()
        lab_type = lab["lab_type"]
        
        # Step 3: Record start usage event in Usage Analytics Service
        start_event = {
            "user_id": user_id,
            "lab_type": lab_type,
            "event_type": "start",
            "event_data": {"session_id": "integration-test-session"}
        }
        start_response = http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=start_event)
        assert start_response.status_code == HTTPStatus.OK
        
        # Step 4: Record lab attempt in User Progress Service
        attempt_data = {
            "user_id": user_id,
            "lab_type": lab_type,
            "completion_status": True,
            "time_spent": 450,
            "errors_encountered": ["permission_denied", "file_not_found"]
        }
        attempt_response = http_client.post(f"{USER_PROGRESS_URL}/progress/lab-attempt", json=attempt_data)
        assert attempt_response.status_code == HTTPStatus.OK
        
        # Step 5: Record performance data in Performance Reporting Service
        performance_data = {
            "user_id": user_id,
            "lab_type": lab_type,
            "completion_time": 450,
            "success": True,
            "errors": ["permission_denied", "file_not_found"],
            "resources_used": {"memory": 256, "cpu": 30}
        }
        perf_response = http_client.post(f"{PERFORMANCE_REPORTING_URL}/performance/record", json=performance_data)
        assert perf_response.status_code == HTTPStatus.OK
        
        # Step 6: Record completion usage event in Usage Analytics Service
        complete_event = {
            "user_id": user_id,
            "lab_type": lab_type,
            "event_type": "complete",
            "event_data": {"session_id": "integration-test-session", "time_spent": 450}
        }
        complete_response = http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=complete_event)
        assert complete_response.status_code == HTTPStatus.OK
        
        # Step 7: Verify user progress in User Progress Service
        time.sleep(1)  # Give a moment for data to be processed
        progress_response = http_client.get(f"{USER_PROGRESS_URL}/progress/{user_id}")
        assert progress_response.status_code == HTTPStatus.OK
        progress = progress_response.json()
        assert len(progress) > 0
        assert progress[0]["user_id"] == user_id
        assert progress[0]["lab_type"] == lab_type
        assert progress[0]["completion_status"] == True
        
        # Step 8: Verify user statistics in User Progress Service
        stats_response = http_client.get(f"{USER_PROGRESS_URL}/progress/stats/{user_id}")
        assert stats_response.status_code == HTTPStatus.OK
        stats = stats_response.json()
        assert stats["user_id"] == user_id
        assert stats["total_attempts"] > 0
        assert stats["success_rate"] > 0
        
        # Step 9: Verify performance metrics in Performance Reporting Service
        perf_metrics_response = http_client.get(f"{PERFORMANCE_REPORTING_URL}/performance/lab/{lab_type}")
        assert perf_metrics_response.status_code == HTTPStatus.OK
        perf_metrics = perf_metrics_response.json()
        assert perf_metrics["lab_type"] == lab_type
        assert perf_metrics["total_users"] > 0
        assert perf_metrics["avg_completion_time"] > 0
        
        # Step 10: Verify user performance in Performance Reporting Service
        user_perf_response = http_client.get(f"{PERFORMANCE_REPORTING_URL}/performance/user/{user_id}")
        assert user_perf_response.status_code == HTTPStatus.OK
        user_perf = user_perf_response.json()
        assert user_perf["user_id"] == user_id
        assert lab_type in user_perf["performance_by_lab"]
        
        # Step 11: Verify lab usage analytics in Usage Analytics Service
        lab_usage_response = http_client.get(f"{USAGE_ANALYTICS_URL}/analytics/usage/lab/{lab_type}")
        assert lab_usage_response.status_code == HTTPStatus.OK
        lab_usage = lab_usage_response.json()
        assert lab_usage["lab_type"] == lab_type
        assert lab_usage["total_events"] >= 2  # We recorded at least start and complete
        
        # Step 12: Verify platform trends in Usage Analytics Service
        trends_response = http_client.get(f"{USAGE_ANALYTICS_URL}/analytics/trends")
        assert trends_response.status_code == HTTPStatus.OK
        trends = trends_response.json()
        assert lab_type in trends["lab_usage"]
        assert trends["lab_usage"][lab_type]["total_events"] >= 2
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_validation_across_services(self, http_client):
        """Test validation across services with invalid data."""
        # Test with non-existent user ID
        fake_user_id = "11111111-2222-3333-4444-555555555555"
        
        # Try to create lab attempt with fake user
        attempt_data = {
            "user_id": fake_user_id,
            "lab_type": "test-lab",
            "completion_status": True,
            "time_spent": 300,
            "errors_encountered": ["test_error"]
        }
        
        attempt_response = http_client.post(
            f"{USER_PROGRESS_URL}/progress/lab-attempt", 
            json=attempt_data
        )
        assert attempt_response.status_code == HTTPStatus.NOT_FOUND
        
        # Try to record performance with fake user
        performance_data = {
            "user_id": fake_user_id,
            "lab_type": "test-lab",
            "completion_time": 300,
            "success": True,
            "errors": ["test_error"],
            "resources_used": {"memory": 128, "cpu": 20}
        }
        
        perf_response = http_client.post(
            f"{PERFORMANCE_REPORTING_URL}/performance/record", 
            json=performance_data
        )
        assert perf_response.status_code == HTTPStatus.NOT_FOUND
        
        # Try to record usage event with fake user
        event_data = {
            "user_id": fake_user_id,
            "lab_type": "test-lab",
            "event_type": "start",
            "event_data": {"session_id": "fake-session"}
        }
        
        event_response = http_client.post(
            f"{USAGE_ANALYTICS_URL}/analytics/event", 
            json=event_data
        )
        assert event_response.status_code == HTTPStatus.NOT_FOUND
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_user_data_consistency(self, test_user_data, test_lab_data, http_client):
        """Test that user data is consistent across services via their validation mechanisms."""
        # First create a user in the User Progress Service
        create_user_response = http_client.post(f"{USER_PROGRESS_URL}/users/", json=test_user_data)
        assert create_user_response.status_code == HTTPStatus.OK
        user = create_user_response.json()
        user_id = user["id"]
        
        # Create a lab in the User Progress Service
        create_lab_response = http_client.post(f"{USER_PROGRESS_URL}/labs/", json=test_lab_data)
        assert create_lab_response.status_code == HTTPStatus.OK
        lab = create_lab_response.json()
        lab_type = lab["lab_type"]
        
        # Test that Performance Reporting Service can validate the user
        performance_data = {
            "user_id": user_id,
            "lab_type": lab_type,
            "completion_time": 300,
            "success": True,
            "errors": ["test_error"],
            "resources_used": {"memory": 128, "cpu": 20}
        }
        
        perf_response = http_client.post(f"{PERFORMANCE_REPORTING_URL}/performance/record", json=performance_data)
        assert perf_response.status_code == HTTPStatus.OK, "Performance service couldn't validate user from User service"
        
        # Test that Usage Analytics Service can validate the user
        event_data = {
            "user_id": user_id,
            "lab_type": lab_type,
            "event_type": "start",
            "event_data": {"session_id": "consistency-test"}
        }
        
        event_response = http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=event_data)
        assert event_response.status_code == HTTPStatus.OK, "Usage Analytics service couldn't validate user from User service"
        
        # Now delete the user and verify that other services can't use it anymore
        delete_user_response = http_client.delete(f"{USER_PROGRESS_URL}/users/{user_id}")
        assert delete_user_response.status_code == HTTPStatus.OK
        
        # Try to use deleted user in Performance Reporting
        time.sleep(1)  # Give a moment for deletion to propagate
        perf_response2 = http_client.post(f"{PERFORMANCE_REPORTING_URL}/performance/record", json=performance_data)
        assert perf_response2.status_code == HTTPStatus.NOT_FOUND, "Performance service didn't recognize deleted user"
        
        # Try to use deleted user in Usage Analytics
        event_response2 = http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=event_data)
        assert event_response2.status_code == HTTPStatus.NOT_FOUND, "Usage Analytics service didn't recognize deleted user"