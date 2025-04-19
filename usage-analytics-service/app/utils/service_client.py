import httpx
import os
from typing import Dict, Any, Optional

USER_SERVICE_URL = os.getenv("USER_PROGRESS_SERVICE_URL", "http://user-progress-service:8000")


# Class to handle requests to other microservices
class ServiceClient:
    # Get user data from the User Progress Service
    @staticmethod
    async def get_user(user_id: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
                if response.status_code == 200:
                    return response.json()
                return None
            except httpx.RequestError:
                return None

    # Get lab data from the User Progress Service
    @staticmethod
    async def get_lab(lab_type: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{USER_SERVICE_URL}/labs/type/{lab_type}")
                if response.status_code == 200:
                    return response.json()
                return None
            except httpx.RequestError:
                return None

    # Validate that a user exists in the User Progress Service
    @staticmethod
    async def validate_user_exists(user_id: str) -> bool:
        user = await ServiceClient.get_user(user_id)
        return user is not None

    # Validate that a lab exists in the User Progress Service
    @staticmethod
    async def validate_lab_exists(lab_type: str) -> bool:
        labs = await ServiceClient.get_lab(lab_type)
        return labs is not None and len(labs) > 0
