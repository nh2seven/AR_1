from fastapi import FastAPI
from app.api import router as api_router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Progress Tracking Service")
app.include_router(api_router)
