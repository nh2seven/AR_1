import os
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from lab_utilization_adapter import LabUtilizationAdapter, IntegrationError as LabIntegrationError
from server_allocation_adapter import ServerAllocationAdapter, IntegrationError as ServerIntegrationError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("integration_api")

# Create the FastAPI app
app = FastAPI(title="Infrastructure Integration API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "service": "Infrastructure Integration API",
        "status": "running",
        "available_endpoints": [
            "/integration/lab-utilization",
            "/integration/lab-utilization/{lab_type}",
            "/integration/server-allocation",
            "/integration/server-allocation/{lab_type}",
        ],
    }


# Utilization endpoints
@app.get("/integration/lab-utilization")
async def get_lab_utilization() -> Dict[str, Any]:
    try:
        return LabUtilizationAdapter.get_enhanced_lab_analytics()
    except LabIntegrationError as e:
        logger.error(f"Integration error fetching lab analytics: {e}")
        raise HTTPException(
            status_code=502,  # Bad Gateway is appropriate for integration failures
            detail=f"Integration failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching enhanced lab analytics: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching enhanced lab analytics: {str(e)}"
        )


@app.get("/integration/lab-utilization/{lab_type}")
async def get_lab_utilization_by_type(lab_type: str) -> Dict[str, Any]:
    try:
        analytics = LabUtilizationAdapter.get_enhanced_lab_analytics()

        # Filter for the specific lab type
        filtered_analytics = {
            "timestamp": analytics.get("timestamp"),
            "lab_usage": {},
            "infrastructure_insights": {"popular_labs": [], "utilization_status": {}},
            "integration_status": analytics.get("integration_status", "success")
        }

        # Extract lab usage data for the specified lab type
        if analytics.get("lab_usage") and lab_type in analytics["lab_usage"]:
            filtered_analytics["lab_usage"][lab_type] = analytics["lab_usage"][lab_type]

        # Extract popular labs data for the specified lab type
        for lab in analytics.get("infrastructure_insights", {}).get("popular_labs", []):
            if lab.get("lab_type") == lab_type:
                filtered_analytics["infrastructure_insights"]["popular_labs"].append(lab)

        # Extract utilization status for the specified lab type
        if lab_type in analytics.get("infrastructure_insights", {}).get("utilization_status", {}):
            filtered_analytics["infrastructure_insights"]["utilization_status"][lab_type] = analytics["infrastructure_insights"]["utilization_status"][lab_type]

        # If we didn't find any relevant data for this lab type, add default data
        if not filtered_analytics["lab_usage"] and not filtered_analytics["infrastructure_insights"]["popular_labs"] and not filtered_analytics["infrastructure_insights"]["utilization_status"]:
            filtered_analytics["lab_usage"][lab_type] = {
                "lab_type": lab_type,
                "time_period_days": 7,
                "unique_users": 0,
                "total_events": 0,
                "event_distribution": {},
                "average_session_time_seconds": 0
            }
            filtered_analytics["integration_status"] = "partial"
            
        return filtered_analytics
    except LabIntegrationError as e:
        logger.error(f"Integration error fetching lab utilization for {lab_type}: {e}")
        raise HTTPException(
            status_code=502,  # Bad Gateway
            detail=f"Integration failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching lab utilization for {lab_type}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching lab utilization for {lab_type}: {str(e)}"
        )


# Server allocation endpoints
@app.get("/integration/server-allocation")
async def get_server_allocation() -> Dict[str, Any]:
    try:
        return ServerAllocationAdapter.get_enhanced_performance_metrics()
    except ServerIntegrationError as e:
        logger.error(f"Integration error fetching performance metrics: {e}")
        raise HTTPException(
            status_code=502,  # Bad Gateway
            detail=f"Integration failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching enhanced performance metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching enhanced performance metrics: {str(e)}",
        )


@app.get("/integration/server-allocation/{lab_type}")
async def get_server_allocation_by_lab(lab_type: str) -> Dict[str, Any]:
    try:
        return ServerAllocationAdapter.get_enhanced_performance_metrics(lab_type=lab_type)
    except ServerIntegrationError as e:
        logger.error(f"Integration error fetching server allocation for {lab_type}: {e}")
        raise HTTPException(
            status_code=502,  # Bad Gateway
            detail=f"Integration failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching server allocation for {lab_type}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching server allocation for {lab_type}: {str(e)}"
        )


if __name__ == "__main__":
    port = int(os.environ.get("INTEGRATION_API_PORT", 8007))
    uvicorn.run(app, host="0.0.0.0", port=port)
