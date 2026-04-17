"""Configuration and data models for the job scraper."""
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# --- DATA MODELS ---

class JobListing(BaseModel):
    """Job listing data model."""
    title: str
    company: str
    location: str
    link: str
    description: str = "N/A"
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    job_board: str = "Unknown"
    match_score: Optional[float] = 0.0

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


class Resume(BaseModel):
    """Resume data model."""
    full_name: str
    email: str
    phone: str = ""
    location: str = ""
    summary: str = ""
    skills: List[str] = Field(default_factory=list)
    experience: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


class JobPreferences(BaseModel):
    """Job preferences for filtering."""
    preferred_job_titles: List[str] = Field(default_factory=list)
    preferred_companies: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    remote_only: bool = False
    minimum_salary: Optional[float] = None
    maximum_salary: Optional[float] = None
    job_boards: List[str] = Field(default_factory=lambda: ["linkedin", "indeed", "glassdoor"])
    required_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    min_match_score: float = 0.6  # 60% match minimum

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True


# --- CONFIGURATION ---

class Config:
    """Application configuration."""
    
    # Google Sheets
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '')
    
    # Scraping
    HEADLESS = True
    TIMEOUT = 30000
    
    # Data paths
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    RESUME_FILE = os.path.join(DATA_DIR, 'resume.pdf')
    PREFERENCES_FILE = os.path.join(DATA_DIR, 'preferences.json')
    JOBS_OUTPUT_FILE = os.path.join(DATA_DIR, 'jobs.json')
