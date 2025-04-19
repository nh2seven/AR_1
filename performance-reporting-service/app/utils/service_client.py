import httpx
import os
from typing import Dict, Any, Optional

# Service URLs - would typically come from environment variables
USER_SERVICE_URL = os.getenv("USER_PROGRESS_SERVICE_URL", "http://user-progress-service:8000")

class ServiceClient:
    """Client for making requests to other microservices"""
    
    @staticmethod
    async def get_user(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data from the User Progress Service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
                if response.status_code == 200:
                    return response.json()
                return None
            except httpx.RequestError:
                return None
    
    @staticmethod
    async def get_lab(lab_type: str) -> Optional[Dict[str, Any]]:
        """Get lab data from the User Progress Service"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{USER_SERVICE_URL}/labs/type/{lab_type}")
                if response.status_code == 200:
                    return response.json()
                return None
            except httpx.RequestError:
                return None
                
    @staticmethod
    async def validate_user_exists(user_id: str) -> bool:
        """Validate that a user exists in the User Progress Service"""
        user = await ServiceClient.get_user(user_id)
        return user is not None
        
    @staticmethod
    async def validate_lab_exists(lab_type: str) -> bool:
        """Validate that a lab exists in the User Progress Service"""
        lab = await ServiceClient.get_lab(lab_type)
        return lab is not None and len(lab) > 0