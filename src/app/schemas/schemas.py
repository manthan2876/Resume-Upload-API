from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

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

class ResumeUploadResponse(BaseModel) :
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
    source: Optional[str] = None
    current_stage: Optional[str] = "Applied"
    hired_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RecruiterDashboard(BaseModel):
    time_to_hire: float
    time_to_fill: float
    sourcing_channel_efficiency: Dict[str, float]
    application_completion_rate: float
    stage_drop_off: Dict[str, int]
    offer_acceptance_rate: float

class HiringManagerDashboard(BaseModel):
    quality_of_hire: float
    interview_to_offer_ratio: float
    candidates_in_progress: Dict[str, int]
    early_turnover_rate: float

class TalentLeaderDashboard(BaseModel):
    cost_per_hire: float
    recruitment_roi: float
    diversity_metrics: Dict[str, Any]
    hiring_volume_vs_plan: Dict[str, int]

class BatchStatus(BaseModel):
    run_id: str
    status: str
    pdfs_processed: int
    total_pdfs: int
    ocr_failed_count: int
    current_stage: str
    start_time: datetime

class SimulationConfig(BaseModel):
    arrival_mode: str = "POISSON"
    rate: float = 1.0
    duration_minutes: int = 60

class RAGQuery(BaseModel):
    question: str
    jd_id: Optional[str] = None
    candidate_ids: Optional[List[int]] = None
