import os
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from lab_utilization_adapter import LabUtilizationAdapter
from server_allocation_adapter import ServerAllocationAdapter

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
    except Exception as e:
        logger.error(f"Error fetching enhanced lab analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching enhanced lab analytics: {str(e)}")


@app.get("/integration/lab-utilization/{lab_type}")
async def get_lab_utilization_by_type(lab_type: str) -> Dict[str, Any]:
    try:
        analytics = LabUtilizationAdapter.get_enhanced_lab_analytics()

        # Filter for the specific lab type
        filtered_analytics = {
            "timestamp": analytics.get("timestamp"),
            "lab_usage": {},
            "infrastructure_insights": {"popular_labs": [], "utilization_status": {}},
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

        return filtered_analytics
    except Exception as e:
        logger.error(f"Error fetching lab utilization for {lab_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching lab utilization for {lab_type}: {str(e)}")


# Server allocation endpoints
@app.get("/integration/server-allocation")
async def get_server_allocation() -> Dict[str, Any]:
    try:
        return ServerAllocationAdapter.get_enhanced_performance_metrics()
    except Exception as e:
        logger.error(f"Error fetching enhanced performance metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching enhanced performance metrics: {str(e)}",
        )


@app.get("/integration/server-allocation/{lab_type}")
async def get_server_allocation_by_lab(lab_type: str) -> Dict[str, Any]:
    try:
        return ServerAllocationAdapter.get_enhanced_performance_metrics(lab_type=lab_type)
    except Exception as e:
        logger.error(f"Error fetching server allocation for {lab_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching server allocation for {lab_type}: {str(e)}")


if __name__ == "__main__":
    port = int(os.environ.get("INTEGRATION_API_PORT", 8007))
    uvicorn.run(app, host="0.0.0.0", port=port)
