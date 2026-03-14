from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import User, UserCreate, UserRole
from app.models.models import DBUser

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = DBUser(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role.value,
        hashed_password=user_in.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
