import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import JobDescription, JobDescriptionCreate, UserRole
from app.models.models import DBUser, DBJobDescription

router = APIRouter(prefix="/api/v1/employers", tags=["Job Descriptions"])

@router.post("/{employer_id}/jd/create", response_model=JobDescription, status_code=status.HTTP_201_CREATED)
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
