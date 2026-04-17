"""
Quick test to verify Google Sheets export works with your credentials
"""
import json
from pathlib import Path
from src.models import JobListing
from src.sheets.integration import SheetsService
from src.utils import setup_logger

logger = setup_logger(__name__)


def test_sheets_export():
    """Test Google Sheets export functionality"""
    logger.info("=" * 60)
    logger.info("Testing Google Sheets Export...")
    logger.info("=" * 60)
    
    # Create sample jobs to export
    sample_jobs = [
        JobListing(
            title="Senior Python Developer",
            company="Tech Corp",
            location="Remote",
            link="https://example.com/job1",
            description="Looking for experienced Python developer",
            salary="$120,000 - $160,000",
            job_type="Full-time",
            source="Indeed",
            match_score=85.5,
            matched_skills=["Python", "Django"],
            missing_skills=["Kubernetes"]
        ),
        JobListing(
            title="ML Engineer",
            company="AI Solutions",
            location="San Francisco, CA",
            link="https://example.com/job2",
            description="Machine Learning Engineer with Python",
            salary="$150,000 - $200,000",
            job_type="Full-time",
            source="LinkedIn",
            match_score=92.0,
            matched_skills=["Python", "AWS"],
            missing_skills=[]
        ),
        JobListing(
            title="Backend Engineer",
            company="Web Corp",
            location="Remote",
            link="https://example.com/job3",
            description="Backend development with Python and Django",
            salary="$100,000 - $140,000",
            job_type="Full-time",
            source="Indeed",
            match_score=78.5,
            matched_skills=["Python", "Docker"],
            missing_skills=["Kubernetes", "AWS"]
        ),
    ]
    
    logger.info(f"Sample jobs created: {len(sample_jobs)}")
    
    # Initialize Sheets service
    sheets = SheetsService()
    
    if not sheets.service:
        logger.error("Google Sheets service not initialized - credentials issue")
        logger.info("\nTo fix this:")
        logger.info("1. Go to Google Cloud Console")
        logger.info("2. Create a service account and download JSON")
        logger.info("3. Set GOOGLE_APPLICATION_CREDENTIALS in .env to the JSON file path")
        logger.info("4. Share the Google Sheet with the service account email")
        return False
    
    # Create headers
    if sheets.create_headers():
        logger.info("Headers created in Google Sheet")
    
    # Append jobs
    if sheets.append_jobs(sample_jobs):
        logger.info(f"Successfully exported {len(sample_jobs)} jobs to Google Sheets!")
        logger.info("\nCheck your Google Sheet:")
        logger.info(f"Sheet ID: {sheets.sheet_id}")
        return True
    else:
        logger.error("Failed to export jobs")
        return False


if __name__ == "__main__":
    test_sheets_export()
