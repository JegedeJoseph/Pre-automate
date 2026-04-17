from pydantic import BaseModel, Field
from typing import Optional, List

class JobPreferences(BaseModel):
    """Job search preferences model"""
    target_titles: List[str] = Field(
        default_factory=list,
        description="Target job titles to search for"
    )
    required_skills: List[str] = Field(
        default_factory=list,
        description="Must-have skills"
    )
    nice_to_have_skills: List[str] = Field(
        default_factory=list,
        description="Nice-to-have skills"
    )
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    locations: List[str] = Field(
        default_factory=list,
        description="Preferred locations"
    )
    remote_preference: str = "any"  # any, remote_only, hybrid, onsite
    job_types: List[str] = Field(
        default_factory=["Full-time"],
        description="Preferred job types"
    )
    excluded_companies: List[str] = Field(
        default_factory=list,
        description="Companies to exclude"
    )
    excluded_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords to exclude from job descriptions"
    )
    min_match_score: float = 60.0  # Minimum match percentage
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_titles": ["Software Engineer", "Backend Developer"],
                "required_skills": ["Python", "Django"],
                "nice_to_have_skills": ["PostgreSQL", "Docker"],
                "min_salary": 80000,
                "max_salary": 150000,
                "locations": ["San Francisco", "Remote"],
                "remote_preference": "hybrid",
                "job_types": ["Full-time", "Contract"],
                "min_match_score": 70.0
            }
        }
