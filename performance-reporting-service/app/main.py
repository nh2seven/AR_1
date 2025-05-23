from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import router as performance_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Performance Reporting Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router without a prefix to match test expectations
app.include_router(performance_router)

# Add a root path handler to avoid 404 on root path
@app.get("/")
async def root():
    return {
        "service": "Performance Reporting Service",
        "status": "running",
        "endpoints": [
            "/performance/record",
            "/performance/lab/{lab_type}",
            "/performance/user/{user_id}"
        ]
    }
