import os
import shutil
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import ResumeUploadResponse
from app.models.models import DBUser, DBResumeInfo, DBJobDescription

router = APIRouter(tags=["Resume Management & Screening"])

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/api/v1/users/{user_id}/resume/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
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

@router.get("/api/v1/users/{user_id}/resume/download/{pdf_id}")
async def download_resume(user_id: int, pdf_id: str, db: Session = Depends(get_db)):
    resume = db.query(DBResumeInfo).filter(DBResumeInfo.pdf_id == pdf_id, DBResumeInfo.user_id == user_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume record not found")
        
    for date_folder in os.listdir(UPLOAD_DIR):
        potential_path = os.path.join(UPLOAD_DIR, date_folder, f"{pdf_id}.pdf")
        if os.path.exists(potential_path):
            return {"download_url": f"https://minio.kenexai.local/resumes/{date_folder}/{pdf_id}.pdf?token=simulated"}
    
    raise HTTPException(status_code=404, detail="Resume file not found in storage")

@router.get("/api/v1/screening/shortlist/{jd_id}")
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
