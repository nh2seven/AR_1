import requests
import json
from typing import Dict, Any, List, Optional
import os
import logging
from datetime import datetime
import time
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("server_allocation_adapter")

# Infrastructure-Microservice endpoints - default to host.docker.internal for containers
RESOURCE_ALLOCATION_BASE_URL = os.getenv("RESOURCE_ALLOCATION_URL", "http://host.docker.internal:3005")
SERVERS_ENDPOINT = f"{RESOURCE_ALLOCATION_BASE_URL}/servers"
ALLOCATIONS_ENDPOINT = f"{RESOURCE_ALLOCATION_BASE_URL}/allocations"

PERFORMANCE_SERVICE_BASE_URL = os.getenv("PERFORMANCE_SERVICE_URL", "http://host.docker.internal:3004")
SERVER_STATS_ENDPOINT = f"{PERFORMANCE_SERVICE_BASE_URL}/performance/servers/stats"
SERVER_PEAKS_ENDPOINT = f"{PERFORMANCE_SERVICE_BASE_URL}/performance/servers"

# Our service endpoint - Use service name for internal docker networking
PERFORMANCE_REPORTING_BASE_URL = os.getenv("PERFORMANCE_REPORTING_URL", "http://performance-reporting:8000")
LAB_PERFORMANCE_ENDPOINT = f"{PERFORMANCE_REPORTING_BASE_URL}/performance/lab"
USER_PERFORMANCE_ENDPOINT = f"{PERFORMANCE_REPORTING_BASE_URL}/performance/user"

# Configure request timeout and retry settings
REQUEST_TIMEOUT = 5  # seconds
MAX_RETRIES = 2
RETRY_DELAY = 1  # seconds

# Cache duration in seconds (5 minutes)
CACHE_DURATION = 300


# Define a custom exception for integration failures
class IntegrationError(Exception):
    pass


"""
INTEGRATION NOTE:
This adapter connects CC_Project's Performance Reporting Service with
Infrastructure-Microservice's Resource Allocation Service.

All calls are made directly to the external API endpoints.
Ensure that both services are running for proper integration.
"""


# Adapter class for integrating performance-reporting-service with resourceAllocation service
class ServerAllocationAdapter:
    _last_fetch_time = {
        "servers": 0,
        "allocations": 0,
        "server_stats": 0,
    }
    _cached_data = {
        "servers": None,
        "allocations": None,
        "server_stats": None,
        "server_peaks": {},
        "lab_performance": {},
        "user_performance": {},
    }

    # Check if cached data should be used based on cache duration
    @classmethod
    def _should_use_cache(cls, cache_key: str) -> bool:
        current_time = time.time()
        return (
            cls._cached_data.get(cache_key) is not None
            and current_time - cls._last_fetch_time.get(cache_key, 0) < CACHE_DURATION
        )

    # Fetch server information from the Infrastructure-Microservice
    @classmethod
    @lru_cache(maxsize=32)
    def get_servers(cls) -> List[Dict[str, Any]]:
        if cls._should_use_cache("servers"):
            logger.info("Using cached server data")
            return cls._cached_data["servers"]

        for attempt in range(MAX_RETRIES + 1):
            try:
                logger.info(f"Fetching server data (attempt {attempt + 1}/{MAX_RETRIES + 1})")
                response = requests.get(SERVERS_ENDPOINT, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                data = response.json()
                logger.info("Successfully connected to Infrastructure-Microservice servers endpoint")

                # Update cache
                cls._cached_data["servers"] = data
                cls._last_fetch_time["servers"] = time.time()

                return data
            except requests.RequestException as e:
                logger.warning(f"Error fetching servers (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All {MAX_RETRIES + 1} attempts to fetch servers failed.")
                    raise IntegrationError(f"Failed to connect to Resource Allocation Service: {str(e)}")

    # Fetch lab-server allocations from the Infrastructure-Microservice
    @classmethod
    @lru_cache(maxsize=32)
    def get_allocations(cls) -> List[Dict[str, Any]]:
        if cls._should_use_cache("allocations"):
            logger.info("Using cached allocation data")
            return cls._cached_data["allocations"]

        for attempt in range(MAX_RETRIES + 1):
            try:
                logger.info(f"Fetching allocation data (attempt {attempt + 1}/{MAX_RETRIES + 1})")
                response = requests.get(ALLOCATIONS_ENDPOINT, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                data = response.json()
                logger.info("Successfully connected to Infrastructure-Microservice allocations endpoint")

                # Update cache
                cls._cached_data["allocations"] = data
                cls._last_fetch_time["allocations"] = time.time()

                return data
            except requests.RequestException as e:
                logger.warning(f"Error fetching allocations (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All {MAX_RETRIES + 1} attempts to fetch allocations failed.")
                    raise IntegrationError(f"Failed to connect to Resource Allocation Service: {str(e)}")

    # Fetch server performance statistics from the Infrastructure-Microservice
    @classmethod
    @lru_cache(maxsize=32)
    def get_server_stats(cls) -> List[Dict[str, Any]]:
        if cls._should_use_cache("server_stats"):
            logger.info("Using cached server stats data")
            return cls._cached_data["server_stats"]

        for attempt in range(MAX_RETRIES + 1):
            try:
                logger.info(f"Fetching server stats data (attempt {attempt + 1}/{MAX_RETRIES + 1})")
                response = requests.get(SERVER_STATS_ENDPOINT, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                data = response.json()
                logger.info("Successfully connected to Infrastructure-Microservice server stats endpoint")

                # Update cache
                cls._cached_data["server_stats"] = data
                cls._last_fetch_time["server_stats"] = time.time()

                return data
            except requests.RequestException as e:
                logger.warning(f"Error fetching server stats (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All {MAX_RETRIES + 1} attempts to fetch server stats failed.")
                    raise IntegrationError(f"Failed to connect to Performance Service: {str(e)}")

    # Fetch peak access times for a specific server from the Infrastructure-Microservice
    @classmethod
    @lru_cache(maxsize=32)
    def get_server_peaks(cls, server_id: int) -> List[Dict[str, Any]]:
        cache_key = f"server_peaks_{server_id}"

        # Check if we should use cached data
        if cache_key in cls._cached_data and cls._should_use_cache(cache_key):
            logger.info(f"Using cached server peaks data for server {server_id}")
            return cls._cached_data[cache_key]

        for attempt in range(MAX_RETRIES + 1):
            try:
                logger.info(f"Fetching server peaks for server {server_id} (attempt {attempt + 1}/{MAX_RETRIES + 1})")
                response = requests.get(f"{SERVER_PEAKS_ENDPOINT}/{server_id}/peaks", timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                data = response.json()
                logger.info(f"Successfully fetched server peaks for server {server_id}")

                # Update cache
                cls._cached_data[cache_key] = data
                cls._last_fetch_time[cache_key] = time.time()

                return data
            except requests.RequestException as e:
                logger.warning(f"Error fetching server peaks for server {server_id} (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"All {MAX_RETRIES + 1} attempts to fetch server peaks for server {server_id} failed.")
                    raise IntegrationError(f"Failed to connect to Performance Service: {str(e)}")

    # Fetch lab performance metrics from our CC_Project's Performance Reporting Service
    @classmethod
    def get_lab_performance(cls, lab_type: str) -> Dict[str, Any]:
        cache_key = f"lab_performance_{lab_type}"
        if cache_key in cls._cached_data and cls._should_use_cache(cache_key):
            logger.info(f"Using cached lab performance data for {lab_type}")
            return cls._cached_data[cache_key]

        try:
            logger.info(f"Fetching lab performance data for {lab_type}")
            response = requests.get(f"{LAB_PERFORMANCE_ENDPOINT}/{lab_type}", timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Successfully fetched lab performance data for {lab_type}")

            # Update cache
            cls._cached_data[cache_key] = data
            cls._last_fetch_time[cache_key] = time.time()

            return data
        except requests.RequestException as e:
            logger.error(f"Error fetching lab performance for {lab_type}: {e}")
            raise IntegrationError(f"Failed to connect to Performance Reporting Service: {str(e)}")

    # Fetch user performance metrics from our CC_Project's Performance Reporting Service
    @classmethod
    def get_user_performance(cls, user_id: str) -> Dict[str, Any]:
        cache_key = f"user_performance_{user_id}"
        if cache_key in cls._cached_data and cls._should_use_cache(cache_key):
            logger.info(f"Using cached user performance data for {user_id}")
            return cls._cached_data[cache_key]

        try:
            logger.info(f"Fetching user performance data for {user_id}")
            response = requests.get(f"{USER_PERFORMANCE_ENDPOINT}/{user_id}", timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Successfully fetched user performance data for {user_id}")

            # Update cache
            cls._cached_data[cache_key] = data
            cls._last_fetch_time[cache_key] = time.time()

            return data
        except requests.RequestException as e:
            logger.error(f"Error fetching user performance for {user_id}: {e}")
            raise IntegrationError(f"Failed to connect to Performance Reporting Service: {str(e)}")

    # Map lab names from Infrastructure-Microservice to our lab types; development mapping, change in production
    @staticmethod
    def map_lab_name_to_type(lab_name: str) -> Optional[str]:
        name_to_type = {
            "Linux Basics": "linux-basics",
            "Networking": "networking",
            "Docker": "docker",
            "Kubernetes": "kubernetes",
            "Filesystem": "filesystem",
            # Add more mappings as needed
        }

        # Try direct mapping from name to type
        for known_name, lab_type in name_to_type.items():
            if known_name.lower() in lab_name.lower():
                return lab_type

        # If no mapping found, generate a generic one based on name
        return lab_name.lower().replace(" ", "-")

    # Get enhanced performance metrics by combining data from both services
    @classmethod
    def get_enhanced_performance_metrics(cls, lab_type: Optional[str] = None) -> Dict[str, Any]:
        try:
            # Get data from Infrastructure-Microservice
            servers = cls.get_servers()
            allocations = cls.get_allocations()
            server_stats = cls.get_server_stats()

            # Build lookup dictionaries for easier access
            server_lookup = {server.get("id"): server for server in servers}

            # Initialize enhanced metrics
            enhanced_metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "labs": {},
                "infrastructure": {"servers": {}, "allocation_map": {}},
                "integration_status": "success",
            }

            # Add server information
            for server in servers:
                server_id = server.get("id")
                if server_id is not None:
                    enhanced_metrics["infrastructure"]["servers"][server_id] = {
                        "name": server.get("name", f"Server-{server_id}"),
                        "specs": {
                            "max_cpu": server.get("max_cpu"),
                            "max_memory": server.get("max_memory"),
                            "max_disk": server.get("max_disk"),
                        },
                        "usage": {
                            "cpu": server.get("cpu_usage"),
                            "memory": server.get("memory_usage"),
                            "disk": server.get("disk_usage"),
                        },
                    }

            # Process allocations and add our performance data
            for allocation in allocations:
                lab_name = allocation.get("lab_name")
                server_id = allocation.get("server_id")

                if lab_name and server_id:
                    lab_type_mapped = cls.map_lab_name_to_type(lab_name)

                    # Skip if we're filtering by lab_type and this isn't it
                    if lab_type and lab_type_mapped != lab_type:
                        continue

                    # Add to allocation map
                    if (lab_type_mapped not in enhanced_metrics["infrastructure"]["allocation_map"]):
                        enhanced_metrics["infrastructure"]["allocation_map"][lab_type_mapped] = []

                    enhanced_metrics["infrastructure"]["allocation_map"][lab_type_mapped].append(server_id)

                    # Get our performance data for this lab
                    if (lab_type_mapped and lab_type_mapped not in enhanced_metrics["labs"]):
                        try:
                            our_lab_performance = cls.get_lab_performance(lab_type_mapped)

                            if our_lab_performance:
                                enhanced_metrics["labs"][lab_type_mapped] = {
                                    "name": lab_name,
                                    "performance": {
                                        "total_users": our_lab_performance.get("total_users", 0),
                                        "avg_completion_time": our_lab_performance.get("avg_completion_time", 0),
                                        "success_rate": our_lab_performance.get("success_rate", 0),
                                        "common_errors": our_lab_performance.get("common_errors", []),
                                    },
                                    "infrastructure": {
                                        "server_id": server_id,
                                        "server_name": server_lookup.get(server_id, {}).get("name", f"Server-{server_id}"),
                                        "resource_allocation": {
                                            "cpu": enhanced_metrics["infrastructure"]["servers"]
                                            .get(server_id, {})
                                            .get("usage", {})
                                            .get("cpu", 0),
                                            "memory": enhanced_metrics["infrastructure"]["servers"]
                                            .get(server_id, {})
                                            .get("usage", {})
                                            .get("memory", 0),
                                            "disk": enhanced_metrics["infrastructure"]["servers"]
                                            .get(server_id, {})
                                            .get("usage", {})
                                            .get("disk", 0),
                                        },
                                    },
                                }

                                # Try to get peak times for this server
                                try:
                                    peaks = cls.get_server_peaks(server_id)
                                    if peaks:
                                        enhanced_metrics["labs"][lab_type_mapped]["infrastructure"]["peak_times"] = peaks
                                except IntegrationError as e:
                                    logger.warning(f"Could not get peak times for server {server_id}: {e}")
                        except IntegrationError as e:
                            logger.warning(f"Could not get performance data for lab {lab_type_mapped}: {e}")

            return enhanced_metrics
        except IntegrationError as e:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_enhanced_performance_metrics: {e}")
            raise IntegrationError(f"Failed to get enhanced performance metrics: {str(e)}")


# Example usage
if __name__ == "__main__":
    adapter = ServerAllocationAdapter()

    try:
        print("Fetching server information...")
        servers = adapter.get_servers()
        print(json.dumps(servers, indent=2))

        print("\nFetching allocation information...")
        allocations = adapter.get_allocations()
        print(json.dumps(allocations, indent=2))

        print("\nFetching enhanced performance metrics...")
        enhanced_metrics = adapter.get_enhanced_performance_metrics()
        print(json.dumps(enhanced_metrics, indent=2))
    except IntegrationError as e:
        print(f"Integration failed: {e}")
