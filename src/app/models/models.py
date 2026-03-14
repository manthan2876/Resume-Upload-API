from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey
from app.core.database import Base

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
    source = Column(String, nullable=True) # LinkedIn, Referral, Indeed, etc.
    current_stage = Column(String, default="Applied") # Applied, Screened, Interview, Offer, Hired, Rejected
    hired_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
