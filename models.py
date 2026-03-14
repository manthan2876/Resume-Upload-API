from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: str # 'employer' or 'employee'

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class Employer(User):
    company_name: str
    industry: Optional[str] = None

class Employee(User):
    skills: List[str] = []
    experience_years: Optional[int] = None
