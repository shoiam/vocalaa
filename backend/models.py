from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserRegister(BaseModel):
    email: str
    password: str
    preferred_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    mcp_slug: str

class BasicInfo(BaseModel):
    name: str
    title: str
    email: EmailStr
    summary: str
    location: Optional[str] = None

class WorkExperience(BaseModel):
    company: str
    role: str
    duration: Optional[str] = None
    description: str
    achievements: Optional[List[str]] = []
    technologies: Optional[List[str]] = []

class Skills(BaseModel):
    programming_languages: List[str]
    frameworks: List[str]
    databases: List[str]

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]
    github_url: Optional[str] = None
    demo_url: Optional[str] = None

class Education(BaseModel):
    institution: str
    degree: str
    field: str
    graduation_year: Optional[int] = None


class ProfileCreate(BaseModel):
    basic_info: BasicInfo
    work_experience: List[WorkExperience]
    skills: Skills
    projects: List[Project]
    education: List[Education]

class Profile(ProfileCreate):
    id: str
    user_id: str
    mcp_slug: str
    created_at: datetime
    updated_at: datetime