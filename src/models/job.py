from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class JobListing(BaseModel):
    """Data model for a job listing"""
    title: str
    company: str
    location: str
    link: str
    description: str = "N/A"
    salary: Optional[str] = None
    job_type: Optional[str] = None  # Full-time, Part-time, Contract, etc.
    required_skills: List[str] = Field(default_factory=list)
    posted_date: Optional[str] = None
    source: str = "Unknown"  # Indeed, LinkedIn, Glassdoor, etc.
    match_score: Optional[float] = 0.0
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    scraped_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "link": "https://example.com/job/123",
                "description": "We are looking for...",
                "salary": "$120,000 - $160,000",
                "job_type": "Full-time",
                "required_skills": ["Python", "Django", "PostgreSQL"],
                "source": "Indeed",
                "match_score": 85.5
            }
        }
