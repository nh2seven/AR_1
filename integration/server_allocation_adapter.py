import requests
import json
from typing import Dict, Any, List, Optional
import os
import logging
from datetime import datetime
import time
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("server_allocation_adapter")

# Infrastructure-Microservice endpoints
RESOURCE_ALLOCATION_BASE_URL = os.getenv("RESOURCE_ALLOCATION_URL", "http://localhost:3005")
SERVERS_ENDPOINT = f"{RESOURCE_ALLOCATION_BASE_URL}/servers"
ALLOCATIONS_ENDPOINT = f"{RESOURCE_ALLOCATION_BASE_URL}/allocations"

PERFORMANCE_SERVICE_BASE_URL = os.getenv("PERFORMANCE_SERVICE_URL", "http://localhost:3004")
SERVER_STATS_ENDPOINT = f"{PERFORMANCE_SERVICE_BASE_URL}/performance/servers/stats"
SERVER_PEAKS_ENDPOINT = f"{PERFORMANCE_SERVICE_BASE_URL}/performance/servers"

# Our service endpoint
PERFORMANCE_REPORTING_BASE_URL = os.getenv("PERFORMANCE_REPORTING_URL", "http://localhost:8005")
LAB_PERFORMANCE_ENDPOINT = f"{PERFORMANCE_REPORTING_BASE_URL}/performance/lab"
USER_PERFORMANCE_ENDPOINT = f"{PERFORMANCE_REPORTING_BASE_URL}/performance/user"

# Configure request timeout and retry settings
REQUEST_TIMEOUT = 5  # seconds
MAX_RETRIES = 2
RETRY_DELAY = 1  # seconds

# Cache duration in seconds (5 minutes)
CACHE_DURATION = 300

"""
INTEGRATION NOTE:
This adapter connects CC_Project's Performance Reporting Service with
Infrastructure-Microservice's Resource Allocation Service.

All calls are made directly to the external API endpoints.
Ensure that both services are running for proper integration.
"""

class ServerAllocationAdapter:
    """
    Adapter class for integrating CC_Project's Performance Reporting Service with 
    Infrastructure-Microservice's Resource Allocation Service.
    """
    
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
    
    @classmethod
    def _should_use_cache(cls, cache_key: str) -> bool:
        """Check if we should use cached data based on cache duration"""
        current_time = time.time()
        return (
            cls._cached_data.get(cache_key) is not None
            and current_time - cls._last_fetch_time.get(cache_key, 0) < CACHE_DURATION
        )
    
    @classmethod
    @lru_cache(maxsize=32)
    def get_servers(cls) -> List[Dict[str, Any]]:
        """
        Fetch server information from the Infrastructure-Microservice.
        
        Returns:
            List of servers with their specifications and usage
        """
        # Check if we should use cached data
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
                    return []
    
    @classmethod
    @lru_cache(maxsize=32)
    def get_allocations(cls) -> List[Dict[str, Any]]:
        """
        Fetch lab-server allocations from the Infrastructure-Microservice.
        
        Returns:
            List of lab-server allocations
        """
        # Check if we should use cached data
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
                    return []
    
    @classmethod
    @lru_cache(maxsize=32)
    def get_server_stats(cls) -> List[Dict[str, Any]]:
        """
        Fetch server performance statistics from the Infrastructure-Microservice.
        
        Returns:
            List of server performance statistics
        """
        # Check if we should use cached data
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
                    return []
    
    @classmethod
    @lru_cache(maxsize=32)
    def get_server_peaks(cls, server_id: int) -> List[Dict[str, Any]]:
        """
        Fetch peak access times for a specific server from the Infrastructure-Microservice.
        
        Args:
            server_id: ID of the server to fetch peak times for
            
        Returns:
            List of peak access times for the server
        """
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
                    return []
    
    @classmethod
    def get_lab_performance(cls, lab_type: str) -> Dict[str, Any]:
        """
        Fetch lab performance metrics from our CC_Project's Performance Reporting Service.
        
        Args:
            lab_type: Type of lab to fetch performance metrics for
            
        Returns:
            Lab performance metrics
        """
        cache_key = f"lab_performance_{lab_type}"
        
        # Check if we should use cached data
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
            return {}
    
    @classmethod
    def get_user_performance(cls, user_id: str) -> Dict[str, Any]:
        """
        Fetch user performance metrics from our CC_Project's Performance Reporting Service.
        
        Args:
            user_id: ID of the user to fetch performance metrics for
            
        Returns:
            User performance metrics
        """
        cache_key = f"user_performance_{user_id}"
        
        # Check if we should use cached data
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
            return {}
    
    @staticmethod
    def map_lab_name_to_type(lab_name: str) -> Optional[str]:
        """
        Maps an Infrastructure-Microservice lab name to our CC_Project lab type.
        In a real implementation, this would involve a proper mapping strategy.
        
        Args:
            lab_name: The lab name from Infrastructure-Microservice
            
        Returns:
            Corresponding lab_type in our system, or None if no mapping exists
        """
        # This is a simplified example; in production, you'd need a more robust mapping
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
    
    @classmethod
    def get_enhanced_performance_metrics(cls, lab_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Combines data from both services to provide enhanced performance metrics.
        
        Args:
            lab_type: Optional lab type to filter results for
            
        Returns:
            Enhanced performance metrics combining data from both systems
        """
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
            "infrastructure": {
                "servers": {},
                "allocation_map": {}
            }
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
                        "max_disk": server.get("max_disk")
                    },
                    "usage": {
                        "cpu": server.get("cpu_usage"),
                        "memory": server.get("memory_usage"),
                        "disk": server.get("disk_usage")
                    }
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
                if lab_type_mapped not in enhanced_metrics["infrastructure"]["allocation_map"]:
                    enhanced_metrics["infrastructure"]["allocation_map"][lab_type_mapped] = []
                
                enhanced_metrics["infrastructure"]["allocation_map"][lab_type_mapped].append(server_id)
                
                # Get our performance data for this lab
                if lab_type_mapped and lab_type_mapped not in enhanced_metrics["labs"]:
                    our_lab_performance = cls.get_lab_performance(lab_type_mapped)
                    
                    if our_lab_performance:
                        # Add our performance data
                        enhanced_metrics["labs"][lab_type_mapped] = {
                            "name": lab_name,
                            "performance": {
                                "total_users": our_lab_performance.get("total_users", 0),
                                "avg_completion_time": our_lab_performance.get("avg_completion_time", 0),
                                "success_rate": our_lab_performance.get("success_rate", 0),
                                "common_errors": our_lab_performance.get("common_errors", [])
                            },
                            "infrastructure": {
                                "server_id": server_id,
                                "server_name": server_lookup.get(server_id, {}).get("name", f"Server-{server_id}"),
                                "resource_allocation": {
                                    "cpu": enhanced_metrics["infrastructure"]["servers"].get(server_id, {}).get("usage", {}).get("cpu", 0),
                                    "memory": enhanced_metrics["infrastructure"]["servers"].get(server_id, {}).get("usage", {}).get("memory", 0),
                                    "disk": enhanced_metrics["infrastructure"]["servers"].get(server_id, {}).get("usage", {}).get("disk", 0)
                                }
                            }
                        }
                        
                        # Try to get peak times for this server
                        try:
                            peaks = cls.get_server_peaks(server_id)
                            if peaks:
                                enhanced_metrics["labs"][lab_type_mapped]["infrastructure"]["peak_times"] = peaks
                        except Exception as e:
                            logger.warning(f"Could not get peak times for server {server_id}: {e}")
        
        return enhanced_metrics


# Example usage
if __name__ == "__main__":
    # Test the adapter
    adapter = ServerAllocationAdapter()
    
    print("Fetching server information...")
    servers = adapter.get_servers()
    print(json.dumps(servers, indent=2))
    
    print("\nFetching allocation information...")
    allocations = adapter.get_allocations()
    print(json.dumps(allocations, indent=2))
    
    print("\nFetching enhanced performance metrics...")
    enhanced_metrics = adapter.get_enhanced_performance_metrics()
    print(json.dumps(enhanced_metrics, indent=2))