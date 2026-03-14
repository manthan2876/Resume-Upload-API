from fastapi import APIRouter
from app.schemas.schemas import SimulationConfig

router = APIRouter(tags=["Simulation & Ingestion"])

@router.post("/api/v1/simulation/start")
async def start_simulation(config: SimulationConfig):
    return {"message": f"Simulation started with {config.arrival_mode} arrival", "rate": config.rate}

@router.post("/api/v1/ingestion/datasets/kaggle")
async def ingest_kaggle_dataset(dataset_url: str):
    return {"message": "Kaggle dataset ingestion triggered", "status": "PENDING"}
