from fastapi import FastAPI
from app.api import router as api_router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Progress Tracking Service")
# Include the router without a prefix to match test expectations
app.include_router(api_router)

# Add a root path handler to avoid 404 on root path
@app.get("/")
async def root():
    return {
        "service": "User Progress Tracking Service",
        "status": "running", 
        "endpoints": [
            "/users/", 
            "/labs/", 
            "/progress/"
        ]
    }
