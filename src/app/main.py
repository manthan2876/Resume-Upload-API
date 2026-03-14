from fastapi import FastAPI
from app.core.database import engine, Base
from app.api import (
    auth, jobs, resumes, pipeline, analytics, ml, 
    privacy, augmentation, simulation, chat, warehouse, infrastructure
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kenexai Talent Analytics Platform API",
    description="API Specification for an AI-Powered Resume Screening and Talent Analytics Platform with PostgreSQL",
    version="1.1.0"
)

# Include Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(resumes.router)
app.include_router(pipeline.router)
app.include_router(analytics.router)
app.include_router(ml.router)
app.include_router(privacy.router)
app.include_router(augmentation.router)
app.include_router(simulation.router)
app.include_router(chat.router)
app.include_router(warehouse.router)
app.include_router(infrastructure.router)

@app.get("/", tags=["General"])
def read_root():
    return {"message": "Kenexai Talent Analytics Platform API with PostgreSQL is online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
