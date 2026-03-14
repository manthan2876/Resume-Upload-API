import uuid
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, HTTPException, Query
from app.schemas.schemas import BatchStatus

router = APIRouter(prefix="/api/v1/pipeline", tags=["Pipeline"])

# In-memory storage for non-persistent batch jobs
batch_jobs: Dict[str, BatchStatus] = {}

@router.post("/daily/extract-text", response_model=BatchStatus, status_code=202)
async def trigger_text_extraction(date: str = Query(..., description="Date to process in YYYY-MM-DD format")):
    run_id = str(uuid.uuid4())
    status_obj = BatchStatus(
        run_id=run_id,
        status="RUNNING",
        pdfs_processed=0,
        total_pdfs=10, 
        ocr_failed_count=0,
        current_stage="EXTRACTION",
        start_time=datetime.now()
    )
    batch_jobs[run_id] = status_obj
    return status_obj

@router.post("/daily/extract-info", response_model=BatchStatus, status_code=202)
async def trigger_info_extraction(run_id: str):
    if run_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")
    batch_jobs[run_id].current_stage = "STRUCTURING"
    return batch_jobs[run_id]

@router.post("/daily/calculate-scores", status_code=202)
async def calculate_scores(jd_id: str):
    """(AI Logic placeholder)"""
    return {"message": "Scoring calculation triggered", "jd_id": jd_id}

@router.get("/status/{run_id}", response_model=BatchStatus)
async def get_pipeline_status(run_id: str):
    if run_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")
    job = batch_jobs[run_id]
    if job.pdfs_processed < job.total_pdfs:
        job.pdfs_processed += 1
    else:
        job.status = "COMPLETED"
    return job
