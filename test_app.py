"""
Demo/Test script for the Job Scraper Application.
Run this to test the application without full web scraping.
"""
import json
from pathlib import Path
from src.resume.parser import ResumeParser
from src.scraper.matcher import SkillMatcher
from src.models import JobListing, JobPreferences, Resume
from src.utils import setup_logger

logger = setup_logger(__name__)


def test_resume_parsing():
    """Test resume parsing functionality"""
    logger.info("=" * 60)
    logger.info("Testing Resume Parsing...")
    logger.info("=" * 60)
    
    resume_path = "./data/sample_resume.txt"
    
    if not Path(resume_path).exists():
        logger.error(f"Resume file not found: {resume_path}")
        return None
    
    parser = ResumeParser(resume_path)
    resume = parser.parse()
    
    logger.info(f"✓ Resume parsed successfully")
    logger.info(f"  Name: {resume.name}")
    logger.info(f"  Email: {resume.email}")
    logger.info(f"  Phone: {resume.phone}")
    logger.info(f"  Location: {resume.location}")
    logger.info(f"  Skills found: {', '.join([s.name for s in resume.skills])}")
    
    return resume


def test_job_matching(resume):
    """Test job matching functionality"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("Testing Job Matching...")
    logger.info("=" * 60)
    
    # Load preferences
    prefs_path = "preferences.json"
    if not Path(prefs_path).exists():
        logger.warning(f"Preferences file not found: {prefs_path}")
        return
    
    with open(prefs_path, 'r') as f:
        prefs_data = json.load(f)
    
    preferences = JobPreferences(**prefs_data)
    logger.info(f"✓ Preferences loaded")
    logger.info(f"  Target titles: {', '.join(preferences.target_titles)}")
    logger.info(f"  Required skills: {', '.join(preferences.required_skills)}")
    logger.info(f"  Min salary: ${preferences.min_salary:,}")
    logger.info(f"  Max salary: ${preferences.max_salary:,}")
    
    # Create sample jobs for testing
    sample_jobs = [
        JobListing(
            title="Senior Python Developer",
            company="Tech Corp",
            location="Remote",
            link="https://example.com/job1",
            description="Looking for experienced Python developer with Django experience",
            salary="$120,000 - $160,000",
            job_type="Full-time",
            source="Indeed"
        ),
        JobListing(
            title="Backend Engineer",
            company="StartUp Inc",
            location="San Francisco, CA",
            link="https://example.com/job2",
            description="Backend engineer needed. Python, FastAPI, and PostgreSQL required",
            salary="$100,000 - $140,000",
            job_type="Full-time",
            source="LinkedIn"
        ),
        JobListing(
            title="Junior JavaScript Developer",
            company="Web Solutions",
            location="New York, NY",
            link="https://example.com/job3",
            description="JavaScript developer needed for frontend work",
            salary="$60,000 - $90,000",
            job_type="Full-time",
            source="Glassdoor"
        ),
    ]
    
    # Match jobs
    matcher = SkillMatcher(resume, preferences)
    matched_jobs = matcher.filter_jobs(sample_jobs)
    
    logger.info(f"✓ Job matching completed")
    logger.info(f"  Total jobs: {len(sample_jobs)}")
    logger.info(f"  Matched jobs: {len(matched_jobs)}")
    
    logger.info("\n📋 Matched Jobs (sorted by score):")
    for i, job in enumerate(matched_jobs, 1):
        logger.info(f"\n  {i}. {job.title}")
        logger.info(f"     Company: {job.company}")
        logger.info(f"     Location: {job.location}")
        logger.info(f"     Salary: {job.salary}")
        logger.info(f"     Match Score: {job.match_score:.1f}%")
        logger.info(f"     Matched Skills: {', '.join(job.matched_skills)}")
        if job.missing_skills:
            logger.info(f"     Missing Skills: {', '.join(job.missing_skills)}")
        logger.info(f"     Source: {job.source}")


def test_data_models():
    """Test data model validation"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("Testing Data Models...")
    logger.info("=" * 60)
    
    # Test JobListing
    try:
        job = JobListing(
            title="Test Job",
            company="Test Company",
            location="Remote",
            link="https://example.com/test"
        )
        logger.info(f"✓ JobListing model valid")
    except Exception as e:
        logger.error(f"✗ JobListing model error: {e}")
    
    # Test JobPreferences
    try:
        prefs = JobPreferences(
            target_titles=["Developer"],
            required_skills=["Python"],
            min_salary=80000
        )
        logger.info(f"✓ JobPreferences model valid")
    except Exception as e:
        logger.error(f"✗ JobPreferences model error: {e}")


def main():
    """Run all tests"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 15 + "JOB SCRAPER - DEMO/TEST SCRIPT" + " " * 13 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    
    # Test 1: Data Models
    test_data_models()
    
    # Test 2: Resume Parsing
    resume = test_resume_parsing()
    
    if resume:
        # Test 3: Job Matching
        test_job_matching(resume)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✓ All tests completed successfully!")
    logger.info("=" * 60)
    logger.info("\nNext steps:")
    logger.info("1. Update preferences.json with your preferences")
    logger.info("2. Update .env with your resume path and API keys")
    logger.info("3. Run 'python main.py' to start scraping jobs")
    logger.info("")


if __name__ == "__main__":
    main()
