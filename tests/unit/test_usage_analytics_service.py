import pytest
import httpx
import os
from http import HTTPStatus

# Service URLs
USER_PROGRESS_URL = os.getenv("USER_PROGRESS_URL", "http://localhost:8004")
USAGE_ANALYTICS_URL = os.getenv("USAGE_ANALYTICS_URL", "http://localhost:8006")

class TestUsageAnalyticsService:
    """Tests for the Usage Analytics Service endpoints."""
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_record_event(self, created_test_user, created_test_lab, http_client):
        """Test recording a usage event."""
        event_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "event_type": "start",
            "event_data": {"session_id": "test-session-1"}
        }
        
        response = http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=event_data)
        assert response.status_code == HTTPStatus.OK, f"Failed to record event: {response.text}"
        
        event = response.json()
        assert event["user_id"] == created_test_user["id"]
        assert event["lab_type"] == created_test_lab["lab_type"]
        assert event["event_type"] == "start"
        assert "id" in event, "Event ID not returned in response"
        assert "timestamp" in event, "Timestamp not returned in response"
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_record_complete_event(self, created_test_user, created_test_lab, http_client):
        """Test recording a completion event."""
        event_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "event_type": "complete",
            "event_data": {"session_id": "test-session-1", "time_spent": 320}
        }
        
        response = http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=event_data)
        assert response.status_code == HTTPStatus.OK, f"Failed to record completion event: {response.text}"
        
        event = response.json()
        assert event["user_id"] == created_test_user["id"]
        assert event["event_type"] == "complete"
        assert "event_data" in event
        assert event["event_data"].get("time_spent") == 320
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_record_error_event(self, created_test_user, created_test_lab, http_client):
        """Test recording an error event."""
        event_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "event_type": "error",
            "event_data": {"error_type": "runtime_error", "error_message": "Test error message"}
        }
        
        response = http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=event_data)
        assert response.status_code == HTTPStatus.OK, f"Failed to record error event: {response.text}"
        
        event = response.json()
        assert event["user_id"] == created_test_user["id"]
        assert event["event_type"] == "error"
        assert "event_data" in event
        assert "error_type" in event["event_data"]
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_get_lab_usage(self, created_test_user, created_test_lab, http_client):
        """Test getting lab usage analytics."""
        # First record start and complete events for the lab
        start_event = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "event_type": "start",
            "event_data": {"session_id": "test-session-2"}
        }
        http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=start_event)
        
        complete_event = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "event_type": "complete",
            "event_data": {"session_id": "test-session-2", "time_spent": 350}
        }
        http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=complete_event)
        
        # Get lab usage
        response = http_client.get(f"{USAGE_ANALYTICS_URL}/analytics/usage/lab/{created_test_lab['lab_type']}")
        assert response.status_code == HTTPStatus.OK, f"Failed to get lab usage: {response.text}"
        
        usage = response.json()
        assert usage["lab_type"] == created_test_lab["lab_type"]
        assert "unique_users" in usage
        assert usage["unique_users"] > 0
        assert "total_events" in usage
        assert usage["total_events"] > 0
        assert "event_distribution" in usage
        assert "start" in usage["event_distribution"]
        assert "complete" in usage["event_distribution"]
        assert "average_session_time_seconds" in usage
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_get_usage_trends(self, created_test_user, created_test_lab, http_client):
        """Test getting platform-wide usage trends."""
        # First record a few events
        for event_type in ["start", "complete", "error"]:
            event_data = {
                "user_id": created_test_user["id"],
                "lab_type": created_test_lab["lab_type"],
                "event_type": event_type,
                "event_data": {"session_id": f"test-session-{event_type}"}
            }
            http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=event_data)
        
        # Get usage trends
        response = http_client.get(f"{USAGE_ANALYTICS_URL}/analytics/trends")
        assert response.status_code == HTTPStatus.OK, f"Failed to get usage trends: {response.text}"
        
        trends = response.json()
        assert "time_period_days" in trends
        assert "total_events" in trends
        assert "lab_usage" in trends
        assert created_test_lab["lab_type"] in trends["lab_usage"]
        
        lab_usage = trends["lab_usage"][created_test_lab["lab_type"]]
        assert "total_events" in lab_usage
        assert "unique_users" in lab_usage
        assert "errors" in lab_usage
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_update_event(self, created_test_user, created_test_lab, http_client):
        """Test updating a usage event."""
        # First create an event
        original_event = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "event_type": "start",
            "event_data": {"session_id": "test-session-3"}
        }
        
        create_response = http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=original_event)
        event = create_response.json()
        event_id = event["id"]
        
        # Update the event
        updated_event = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "event_type": "start",
            "event_data": {"session_id": "test-session-3-modified", "additional_data": "test"}
        }
        
        response = http_client.put(f"{USAGE_ANALYTICS_URL}/analytics/event/{event_id}", json=updated_event)
        assert response.status_code == HTTPStatus.OK, f"Failed to update event: {response.text}"
        
        updated = response.json()
        assert updated["id"] == event_id
        assert updated["event_data"]["session_id"] == "test-session-3-modified"
        assert updated["event_data"]["additional_data"] == "test"
    
    @pytest.mark.usefixtures("wait_for_services")
    def test_delete_event(self, created_test_user, created_test_lab, http_client):
        """Test deleting a usage event."""
        # First create an event
        event_data = {
            "user_id": created_test_user["id"],
            "lab_type": created_test_lab["lab_type"],
            "event_type": "start",
            "event_data": {"session_id": "test-session-to-delete"}
        }
        
        create_response = http_client.post(f"{USAGE_ANALYTICS_URL}/analytics/event", json=event_data)
        event = create_response.json()
        event_id = event["id"]
        
        # Delete the event
        response = http_client.delete(f"{USAGE_ANALYTICS_URL}/analytics/event/{event_id}")
        assert response.status_code == HTTPStatus.OK, f"Failed to delete event: {response.text}"
        
        # Verify deletion
        result = response.json()
        assert result["status"] == "success"
        assert f"Event {event_id} deleted" in result["message"]