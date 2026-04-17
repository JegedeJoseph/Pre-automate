from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Skills(BaseModel):
    """Skills model"""
    name: str
    proficiency: Optional[str] = "Intermediate"  # Beginner, Intermediate, Advanced, Expert
    years_of_experience: Optional[float] = None

class WorkExperience(BaseModel):
    """Work experience model"""
    job_title: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    skills_used: List[str] = Field(default_factory=list)

class Resume(BaseModel):
    """Resume model"""
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: List[Skills] = Field(default_factory=list)
    experience: List[WorkExperience] = Field(default_factory=list)
    education: Optional[List[str]] = Field(default_factory=list)
    certifications: Optional[List[str]] = Field(default_factory=list)
    file_path: Optional[str] = None
    parsed_at: datetime = Field(default_factory=datetime.now)
    
    def get_skill_names(self) -> List[str]:
        """Get list of all skills"""
        return [skill.name for skill in self.skills]
    
    def get_all_experiences_skills(self) -> List[str]:
        """Get all skills mentioned in work experience"""
        all_skills = []
        for exp in self.experience:
            all_skills.extend(exp.skills_used)
        return list(set(all_skills))
