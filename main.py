import os
import shutil
import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Path, Query, Depends
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import (
    User, UserCreate, JobDescription, JobDescriptionCreate, 
    ResumeUploadResponse, UserRole, ResumeInfo, BatchStatus,
    SimulationConfig, RAGQuery, DashboardKPIs,
    DBUser, DBJobDescription, DBResumeInfo
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kenexai Talent Analytics Platform API",
    description="API Specification for an AI-Powered Resume Screening and Talent Analytics Platform with PostgreSQL",
    version="1.1.0"
)

# In-memory storage for non-persistent batch jobs (In production, use Redis/Task Queue)
batch_jobs: Dict[str, BatchStatus] = {}

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- User Management & Auth ---

@app.post("/api/v1/auth/register", response_model=User, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = DBUser(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role.value,
        hashed_password=user_in.password # In production, use hashing (passlib)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- Job Descriptions ---

@app.post("/api/v1/employers/{employer_id}/jd/create", response_model=JobDescription, status_code=status.HTTP_201_CREATED, tags=["Job Descriptions"])
def create_jd(employer_id: int, jd_in: JobDescriptionCreate, db: Session = Depends(get_db)):
    employer = db.query(DBUser).filter(DBUser.id == employer_id, DBUser.role == UserRole.EMPLOYER.value).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    
    jd_id = str(uuid.uuid4())
    new_jd = DBJobDescription(
        id=jd_id,
        employer_id=employer_id,
        jd_raw_text=jd_in.jd_raw_text,
        jd_metadata=jd_in.jd_metadata
    )
    db.add(new_jd)
    db.commit()
    db.refresh(new_jd)
    return new_jd

# --- Resume Upload & Management (MinIO Integration Simulated) ---

@app.post("/api/v1/users/{user_id}/resume/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED, tags=["Resume Management"])
async def upload_resume(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    pdf_id = str(uuid.uuid4())
    today = datetime.now().strftime("%Y-%m-%d")
    
    bucket_path = os.path.join(UPLOAD_DIR, today)
    if not os.path.exists(bucket_path):
        os.makedirs(bucket_path)
    
    file_path = os.path.join(bucket_path, f"{pdf_id}.pdf")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")
    
    # Store initial record in DB (Bronze layer)
    resume_info = DBResumeInfo(user_id=user_id, pdf_id=pdf_id)
    db.add(resume_info)
    db.commit()
    
    return ResumeUploadResponse(
        pdf_id=pdf_id,
        filename=file.filename,
        upload_date=today,
        bucket="resumes",
        message="Resume uploaded successfully to object storage and metadata persisted"
    )

@app.get("/api/v1/users/{user_id}/resume/download/{pdf_id}", tags=["Resume Management"])
async def download_resume(user_id: int, pdf_id: str, db: Session = Depends(get_db)):
    resume = db.query(DBResumeInfo).filter(DBResumeInfo.pdf_id == pdf_id, DBResumeInfo.user_id == user_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume record not found")
        
    for date_folder in os.listdir(UPLOAD_DIR):
        potential_path = os.path.join(UPLOAD_DIR, date_folder, f"{pdf_id}.pdf")
        if os.path.exists(potential_path):
            return {"download_url": f"https://minio.kenexai.local/resumes/{date_folder}/{pdf_id}.pdf?token=simulated"}
    
    raise HTTPException(status_code=404, detail="Resume file not found in storage")

# --- End-of-Day Batch Processing: Docling Extraction & Structuring ---

@app.post("/api/v1/pipeline/daily/extract-text", response_model=BatchStatus, status_code=status.HTTP_202_ACCEPTED, tags=["Pipeline"])
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

@app.post("/api/v1/pipeline/daily/extract-info", response_model=BatchStatus, status_code=status.HTTP_202_ACCEPTED, tags=["Pipeline"])
async def trigger_info_extraction(run_id: str):
    if run_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")
    batch_jobs[run_id].current_stage = "STRUCTURING"
    return batch_jobs[run_id]

@app.get("/api/v1/pipeline/status/{run_id}", response_model=BatchStatus, tags=["Pipeline"])
async def get_pipeline_status(run_id: str):
    if run_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")
    job = batch_jobs[run_id]
    if job.pdfs_processed < job.total_pdfs:
        job.pdfs_processed += 1
    else:
        job.status = "COMPLETED"
    return job

# --- Machine Learning Scoring & Resume Screening ---

@app.post("/api/v1/pipeline/daily/calculate-scores", tags=["ML Scoring"])
async def calculate_scores(jd_id: str):
    """(AI Logic placeholder)"""
    return {"message": "Scoring calculation triggered", "jd_id": jd_id}

@app.get("/api/v1/screening/shortlist/{jd_id}", tags=["Screening"])
async def get_shortlist(jd_id: str, threshold: float = 60.0, db: Session = Depends(get_db)):
    jd = db.query(DBJobDescription).filter(DBJobDescription.id == jd_id).first()
    if not jd:
        raise HTTPException(status_code=404, detail="Job Description not found")
    
    # Simulate database query with score filtering
    return [
        {
            "user_id": 1,
            "full_name": "John Doe",
            "skill_matched_score": 85.5,
            "resume_score": 90.0,
            "match_status": "Highly Recommended"
        }
    ]

@app.post("/api/v1/ml/generate-embeddings", tags=["ML Scoring"])
async def generate_embeddings(text: str):
    """(AI Logic placeholder)"""
    return {"message": "Embedding generation successful", "vector_dim": 768}

# --- Data Source Simulation & Synthetic Ingestion ---

@app.post("/api/v1/simulation/start", tags=["Simulation"])
async def start_simulation(config: SimulationConfig):
    return {"message": f"Simulation started with {config.arrival_mode} arrival", "rate": config.rate}

@app.post("/api/v1/ingestion/datasets/kaggle", tags=["Ingestion"])
async def ingest_kaggle_dataset(dataset_url: str):
    return {"message": "Kaggle dataset ingestion triggered", "status": "PENDING"}

# --- Data Warehouse: Medallion Architecture ---

@app.post("/api/v1/warehouse/silver/cleanse", tags=["Warehouse"])
async def promote_to_silver():
    return {"message": "Silver layer cleansing complete", "processed_records": 100}

@app.post("/api/v1/warehouse/gold/aggregate", tags=["Warehouse"])
async def aggregate_to_gold():
    return {"message": "Gold layer aggregation complete", "new_metrics": 5}

# --- PII Synthesis, Redaction, and Privacy Compliance ---

@app.post("/api/v1/privacy/detect-pii", tags=["Privacy"])
async def detect_pii(text_id: str):
    """(AI Logic placeholder)"""
    return {"message": "PII detection scan complete", "entities_found": ["NAME", "PHONE"]}

@app.post("/api/v1/privacy/redact-and-synthesize", tags=["Privacy"])
async def redact_and_synthesize(text_id: str):
    """(AI Logic placeholder)"""
    return {"message": "Privacy-compliant synthesis complete", "status": "REDACTED"}

# --- Resume Data Augmentation and Dataset Balancing ---

@app.post("/api/v1/augmentation/textual-variation", tags=["Augmentation"])
async def textual_variation(text: str):
    """(AI Logic placeholder)"""
    return {"message": "Textual variation generated", "status": "AUGMENTED"}

@app.post("/api/v1/augmentation/tabular-smote", tags=["Augmentation"])
async def tabular_smote():
    """(ML Logic placeholder)"""
    return {"message": "Tabular SMOTE augmentation complete", "new_records": 50}

# --- Generative AI and Conversational RAG Chatbot ---

@app.post("/api/v1/rag/ingest-knowledge", tags=["AI Chat"])
async def ingest_knowledge(run_id: str):
    """(AI Logic placeholder)"""
    return {"message": "Knowledge ingestion for RAG triggered", "status": "INDEXING"}

@app.post("/api/v1/chat/query", tags=["AI Chat"])
async def chat_query(query: RAGQuery):
    """(AI Logic placeholder)"""
    return {
        "answer": "Candidate John Doe is highly recommended because of his 5+ years of experience in React and Docker, matching your JD perfectly.",
        "citations": ["resume_123.pdf", "jd_456.txt"]
    }

# --- Analytics Dashboard Endpoints ---

@app.get("/api/v1/analytics/dashboard/screening-yield", response_model=DashboardKPIs, tags=["Analytics"])
async def get_dashboard_metrics():
    return DashboardKPIs(
        screening_yield=75.5,
        skill_gaps={"TensorFlow": 15, "Kubernetes": 10},
        quality_trend=[{"date": "2026-03-01", "avg_score": 82}, {"date": "2026-03-14", "avg_score": 88}]
    )

# --- System Orchestration & Dockerized Deployment ---

@app.get("/api/v1/health/minio", tags=["Infrastructure"])
async def health_minio():
    return {"status": "HEALTHY", "service": "MinIO", "uptime": "49m"}

@app.get("/api/v1/health/docling", tags=["Infrastructure"])
async def health_docling():
    return {"status": "READY", "service": "Docling OCR", "memory_usage": "1.2GB"}

@app.post("/api/v1/webhooks/docling/callback", tags=["Infrastructure"])
async def docling_callback(payload: Dict[str, Any]):
    return {"message": "Callback received", "pdf_id": payload.get("pdf_id")}

# --- Root ---

@app.get("/", tags=["General"])
def read_root():
    return {"message": "Kenexai Talent Analytics Platform API with PostgreSQL is online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
