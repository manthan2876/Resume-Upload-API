from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base

# --- SQLAlchemy Models ---

class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String) # CANDIDATE, EMPLOYER, ADMIN
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now)

class DBJobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(String, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("users.id"))
    jd_raw_text = Column(Text)
    jd_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

class DBResumeInfo(Base):
    __tablename__ = "resumes"
    pdf_id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    skills = Column(JSON, default=[]) # List of strings
    experience_years = Column(Float, nullable=True)
    education = Column(JSON, default=[]) # List of dicts
    raw_text = Column(Text, nullable=True)
    skill_matched_score = Column(Float, nullable=True)
    resume_score = Column(Float, nullable=True)
    jd_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

# --- Pydantic Schemas ---

class UserRole(str, Enum):
    CANDIDATE = "CANDIDATE"
    EMPLOYER = "EMPLOYER"
    ADMIN = "ADMIN"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class JobDescriptionCreate(BaseModel):
    jd_raw_text: str
    jd_metadata: Optional[Dict[str, Any]] = None

class JobDescription(JobDescriptionCreate):
    id: str
    employer_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeUploadResponse(BaseModel):
    pdf_id: str
    filename: str
    upload_date: str
    bucket: str
    message: str

class ResumeInfo(BaseModel):
    user_id: int
    pdf_id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[float] = None
    education: Optional[List[Dict[str, str]]] = None
    raw_text: Optional[str] = None
    skill_matched_score: Optional[float] = None
    resume_score: Optional[float] = None
    jd_id: Optional[str] = None

    class Config:
        from_attributes = True

class BatchStatus(BaseModel):
    run_id: str
    status: str # "RUNNING", "COMPLETED", "FAILED"
    pdfs_processed: int
    total_pdfs: int
    ocr_failed_count: int
    current_stage: str # "EXTRACTION", "STRUCTURING", "SCORING"
    start_time: datetime

class SimulationConfig(BaseModel):
    arrival_mode: str = "POISSON"
    rate: float = 1.0 # applications per minute
    duration_minutes: int = 60

class RAGQuery(BaseModel):
    question: str
    jd_id: Optional[str] = None
    candidate_ids: Optional[List[int]] = None

class DashboardKPIs(BaseModel):
    screening_yield: float
    skill_gaps: Dict[str, int]
    quality_trend: List[Dict[str, Any]]
