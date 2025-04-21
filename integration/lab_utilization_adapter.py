import requests
import json
from typing import Dict, Any, List, Optional
import os
import logging
from datetime import datetime
import time
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("lab_utilization_adapter")

# Infrastructure-Microservice endpoints - get from environment variables or use fallbacks
LAB_MONITORING_BASE_URL = os.getenv("LAB_MONITORING_URL", "http://host.docker.internal:3003")
POPULAR_LABS_ENDPOINT = f"{LAB_MONITORING_BASE_URL}/monitor/labs/popular"
LAB_UTILIZATION_ENDPOINT = f"{LAB_MONITORING_BASE_URL}/monitor/labs/over-under-utilized"

# Our service endpoint - Use service name for internal docker networking
USAGE_ANALYTICS_BASE_URL = os.getenv("USAGE_ANALYTICS_URL", "http://usage-analytics:8000")
USAGE_ANALYTICS_TRENDS_ENDPOINT = f"{USAGE_ANALYTICS_BASE_URL}/analytics/trends"
USAGE_ANALYTICS_LAB_ENDPOINT = f"{USAGE_ANALYTICS_BASE_URL}/analytics/usage/lab"

# Configure request timeout and retry settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "5"))  # seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))  # seconds

# Cache duration in seconds (5 minutes by default)
CACHE_DURATION = int(os.getenv("CACHE_DURATION", "300"))

# Print connection information
logger.info(f"Connecting to Lab Monitoring Service at: {LAB_MONITORING_BASE_URL}")
logger.info(f"Connecting to Usage Analytics Service at: {USAGE_ANALYTICS_BASE_URL}")

# Define a custom exception for integration failures
class IntegrationError(Exception):
    pass

"""
INTEGRATION NOTE:
This adapter connects CC_Project's Usage Analytics Service with
Infrastructure-Microservice's Lab Monitoring Service.

All calls are made directly to the external API endpoints.
Ensure that both services are running for proper integration.
"""


# Adapter class for lab utilization and analytics
class LabUtilizationAdapter:
    _last_fetch_time = {
        "popular_labs": 0,
        "lab_utilization": 0,
        "usage_analytics": 0,
    }
    _cached_data = {
        "popular_labs": None,
        "lab_utilization": None,
        "usage_analytics": {},
    }

    # Check if cached data should be used based on cache duration
    @classmethod
    def _should_use_cache(cls, cache_key: str) -> bool:
        current_time = time.time()
        return (cls._cached_data.get(cache_key) is not None and current_time - cls._last_fetch_time.get(cache_key, 0) < CACHE_DURATION)

    # Fetch popular labs data from the Infrastructure-Microservice
    @classmethod
    @lru_cache(maxsize=32)
    def get_popular_labs(cls) -> List[Dict[str, Any]]:
        if cls._should_use_cache("popular_labs"):
            logger.info("Using cached popular labs data")
            return cls._cached_data["popular_labs"]

        for attempt in range(MAX_RETRIES + 1):
            try:
                logger.info(f"Fetching popular labs data (attempt {attempt + 1}/{MAX_RETRIES + 1})")
                response = requests.get(POPULAR_LABS_ENDPOINT, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                data = response.json()
                logger.info("Successfully connected to Infrastructure-Microservice popular labs endpoint")
                
                # Update cache
                cls._cached_data["popular_labs"] = data
                cls._last_fetch_time["popular_labs"] = time.time()
                
                return data
            except requests.RequestException as e:
                logger.warning(f"Error fetching popular labs (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All {MAX_RETRIES + 1} attempts to fetch popular labs failed.")
                    # Return empty data instead of raising an exception
                    empty_data = []
                    cls._cached_data["popular_labs"] = empty_data
                    cls._last_fetch_time["popular_labs"] = time.time()
                    return empty_data

    # Fetch lab utilization data from the Infrastructure-Microservice
    @classmethod
    @lru_cache(maxsize=32)
    def get_lab_utilization(cls) -> List[Dict[str, Any]]:
        if cls._should_use_cache("lab_utilization"):
            logger.info("Using cached lab utilization data")
            return cls._cached_data["lab_utilization"]

        for attempt in range(MAX_RETRIES + 1):
            try:
                logger.info(f"Fetching lab utilization data (attempt {attempt + 1}/{MAX_RETRIES + 1})")
                response = requests.get(LAB_UTILIZATION_ENDPOINT, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                data = response.json()
                logger.info("Successfully connected to Infrastructure-Microservice lab utilization endpoint")
                
                # Update cache
                cls._cached_data["lab_utilization"] = data
                cls._last_fetch_time["lab_utilization"] = time.time()
                
                return data
            except requests.RequestException as e:
                logger.warning(f"Error fetching lab utilization (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All {MAX_RETRIES + 1} attempts to fetch lab utilization failed.")
                    # Return empty data instead of raising an exception
                    empty_data = []  # Return an empty list of labs instead of raising an exception
                    cls._cached_data["lab_utilization"] = empty_data
                    cls._last_fetch_time["lab_utilization"] = time.time()
                    return empty_data

    # Fetch usage analytics trends from our CC_Project's Usage Analytics Service
    @classmethod
    def get_our_usage_analytics(cls, days: int = 30) -> Dict[str, Any]:
        cache_key = f"usage_analytics_{days}"
        if cache_key in cls._cached_data and cls._should_use_cache(cache_key):
            logger.info(f"Using cached usage analytics data for {days} days")
            return cls._cached_data[cache_key]

        for attempt in range(MAX_RETRIES + 1):
            try:
                logger.info(f"Fetching usage analytics trends for {days} days (attempt {attempt + 1}/{MAX_RETRIES + 1})")
                response = requests.get(f"{USAGE_ANALYTICS_TRENDS_ENDPOINT}?days={days}", timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Successfully fetched usage analytics trends for {days} days")
                
                # Update cache
                cls._cached_data[cache_key] = data
                cls._last_fetch_time[cache_key] = time.time()
                
                return data
            except requests.RequestException as e:
                logger.warning(f"Error fetching usage analytics (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All {MAX_RETRIES + 1} attempts to fetch usage analytics failed.")
                    # Return empty data instead of raising an exception
                    empty_data = {"lab_usage": {}}
                    cls._cached_data[cache_key] = empty_data
                    cls._last_fetch_time[cache_key] = time.time()
                    return empty_data

    # Fetch lab usage data from our CC_Project's Usage Analytics Service
    @staticmethod
    def get_lab_usage(lab_type: str, days: int = 7) -> Dict[str, Any]:
        try:
            response = requests.get(f"{USAGE_ANALYTICS_LAB_ENDPOINT}/{lab_type}?days={days}", timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching lab usage for {lab_type}: {e}")
            # Return empty data instead of raising an exception
            return {
                "lab_type": lab_type,
                "time_period_days": days,
                "unique_users": 0,
                "total_events": 0,
                "event_distribution": {},
                "average_session_time_seconds": 0
            }

    # Map lab ID from Infrastructure-Microservice to our lab type
    @staticmethod
    def map_lab_id_to_type(lab_id: int, lab_name: str) -> Optional[str]:
        name_to_type = {
            "Linux Basics": "linux-basics",
            "Networking": "networking",
            "Docker": "docker",
            "Kubernetes": "kubernetes",
            "Filesystem": "filesystem",
            # Add more mappings as needed
        }

        # Try direct mapping from name to type (simplified)
        for known_name, lab_type in name_to_type.items():
            if known_name.lower() in lab_name.lower():
                return lab_type

        # If no mapping found, generate a generic one based on name
        return lab_name.lower().replace(" ", "-")

    # Fetch enhanced lab analytics by combining data from both services
    @classmethod
    def get_enhanced_lab_analytics(cls) -> Dict[str, Any]:
        # Initialize default response structure
        enhanced_analytics = {
            "timestamp": datetime.utcnow().isoformat(),
            "lab_usage": {},
            "infrastructure_insights": {"popular_labs": [], "utilization_status": {}},
            "integration_status": "success"
        }
        
        try:
            # Get data from both services - these methods now return empty data on failure instead of raising exceptions
            popular_labs = cls.get_popular_labs()
            lab_utilization = cls.get_lab_utilization()
            our_usage_trends = cls.get_our_usage_analytics()

            # Track if we have partial data
            has_infrastructure_data = bool(popular_labs) or bool(lab_utilization)
            has_analytics_data = "lab_usage" in our_usage_trends and bool(our_usage_trends["lab_usage"])
            
            if not has_infrastructure_data and not has_analytics_data:
                enhanced_analytics["integration_status"] = "failed"
            elif not has_infrastructure_data or not has_analytics_data:
                enhanced_analytics["integration_status"] = "partial"

            # Add our analytics data
            if our_usage_trends and "lab_usage" in our_usage_trends:
                enhanced_analytics["lab_usage"] = our_usage_trends["lab_usage"]

            # Add infrastructure insights
            for lab in popular_labs:
                lab_id = lab.get("lab_id")
                name = lab.get("name")
                lab_type = cls.map_lab_id_to_type(lab_id, name)

                if lab_type:
                    enhanced_analytics["infrastructure_insights"]["popular_labs"].append(
                        {
                            "lab_type": lab_type,
                            "name": name,
                            "sessions": lab.get("total_sessions", 0),
                            "user_minutes": lab.get("total_user_minutes", 0),
                        }
                    )

                    # Try to get our usage data for this lab type
                    try:
                        our_lab_data = cls.get_lab_usage(lab_type)
                        if our_lab_data and lab_type not in enhanced_analytics["lab_usage"]:
                            enhanced_analytics["lab_usage"][lab_type] = our_lab_data
                    except Exception as e:
                        logger.warning(f"Could not get our usage data for {lab_type}: {e}")

            # Add utilization status information
            for lab in lab_utilization:
                lab_id = lab.get("lab_id")
                name = lab.get("name")
                lab_type = cls.map_lab_id_to_type(lab_id, name)

                if lab_type:
                    enhanced_analytics["infrastructure_insights"]["utilization_status"][
                        lab_type
                    ] = {
                        "status": lab.get("status"),
                        "avg_users": lab.get("avg_users"),
                        "estimated_users": lab.get("estimated_users"),
                        "ratio": lab.get("ratio"),
                    }

            # Add default data for common lab types if we don't have data
            default_lab_types = ["linux-basics", "docker", "kubernetes", "networking", "filesystem"]
            for lab_type in default_lab_types:
                if lab_type not in enhanced_analytics["lab_usage"]:
                    enhanced_analytics["lab_usage"][lab_type] = {
                        "lab_type": lab_type,
                        "time_period_days": 7,
                        "unique_users": 0,
                        "total_events": 0,
                        "event_distribution": {},
                        "average_session_time_seconds": 0
                    }

            return enhanced_analytics
        except Exception as e:
            # Never fail, provide at least a minimal response
            logger.error(f"Unexpected error in get_enhanced_lab_analytics: {e}")
            enhanced_analytics["integration_status"] = "error"
            enhanced_analytics["error_details"] = str(e)
            return enhanced_analytics


# Example usage
if __name__ == "__main__":
    adapter = LabUtilizationAdapter()

    try:
        print("Fetching popular labs...")
        popular_labs = adapter.get_popular_labs()
        print(json.dumps(popular_labs, indent=2))

        print("\nFetching lab utilization...")
        lab_utilization = adapter.get_lab_utilization()
        print(json.dumps(lab_utilization, indent=2))

        print("\nFetching enhanced analytics...")
        enhanced_analytics = adapter.get_enhanced_lab_analytics()
        print(json.dumps(enhanced_analytics, indent=2))
    except IntegrationError as e:
        print(f"Integration failed: {e}")
