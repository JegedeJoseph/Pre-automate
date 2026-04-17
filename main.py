"""
Job Scraper and Matcher - Main Entry Point
Scrapes job listings from multiple sources and matches them with resume/preferences.
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

from src.resume.parser import ResumeParser
from src.scraper.jobs import JobScraper
from src.scraper.matcher import SkillMatcher
from src.sheets.integration import SheetsService
from src.models import JobPreferences, Resume
from src.utils import setup_logger, Config

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)


class JobScraperApplication:
    """Main application orchestrator for job scraping and matching"""
    
    def __init__(self, resume_path: Optional[str] = None, preferences_path: Optional[str] = None):
        """
        Initialize the application.
        
        Args:
            resume_path: Path to resume file (PDF, DOCX, or TXT)
            preferences_path: Path to preferences JSON file
        """
        self.resume: Optional[Resume] = None
        self.preferences: Optional[JobPreferences] = None
        self.jobs: List = []
        self.matcher: Optional[SkillMatcher] = None
        self.sheets_service = SheetsService()
        self.logger = logger
        
        # Load resume and preferences
        if resume_path:
            self._load_resume(resume_path)
        if preferences_path:
            self._load_preferences(preferences_path)
    
    def _load_resume(self, resume_path: str) -> None:
        """Load and parse resume from file"""
        try:
            if not Path(resume_path).exists():
                self.logger.error(f"Resume file not found: {resume_path}")
                return
            
            parser = ResumeParser(resume_path)
            self.resume = parser.parse()
            self.logger.info(f"Resume loaded successfully from {resume_path}")
            self.logger.info(f"Found skills: {', '.join(self.resume.get_skill_names())}")
        except Exception as e:
            self.logger.error(f"Error loading resume: {e}")
    
    def _load_preferences(self, preferences_path: str) -> None:
        """Load job preferences from JSON file"""
        try:
            if not Path(preferences_path).exists():
                self.logger.error(f"Preferences file not found: {preferences_path}")
                return
            
            with open(preferences_path, 'r') as f:
                prefs_data = json.load(f)
            
            self.preferences = JobPreferences(**prefs_data)
            self.logger.info(f"Preferences loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading preferences: {e}")
    
    async def scrape_jobs_async(
        self,
        search_query: str,
        location: str = "",
        pages: int = 3,
        sources: Optional[List[str]] = None
    ) -> List:
        """
        Scrape jobs from multiple sources asynchronously.
        
        Args:
            search_query: Job search query
            location: Geographic location for search
            pages: Number of pages to scrape per source
            sources: List of sources to scrape (indeed, linkedin, glassdoor)
        
        Returns:
            List of JobListing objects
        """
        self.logger.info(f"Starting job scrape for query: '{search_query}' in {location or 'all locations'}")
        
        scraper = JobScraper()
        jobs = []
        
        if sources is None:
            sources = ["indeed"]  # Default to Indeed if not specified
        
        try:
            jobs = await scraper.scrape_all(
                search_query=search_query,
                location=location,
                pages=pages,
                sources=sources
            )
            self.jobs = jobs
            self.logger.info(f"Scraped {len(jobs)} total jobs")
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
        
        return jobs
    
    def match_and_filter_jobs(self) -> List:
        """Match and filter jobs based on resume and preferences"""
        if not self.resume or not self.preferences:
            self.logger.warning("Resume and preferences must be loaded before matching")
            return []
        
        if not self.jobs:
            self.logger.warning("No jobs to match")
            return []
        
        self.logger.info(f"Matching {len(self.jobs)} jobs with resume...")
        self.matcher = SkillMatcher(self.resume, self.preferences)
        matched_jobs = self.matcher.filter_jobs(self.jobs)
        
        self.logger.info(f"Found {len(matched_jobs)} matching jobs")
        for job in matched_jobs[:5]:
            self.logger.info(
                f"  - {job.title} at {job.company} ({job.location}) - "
                f"Match: {job.match_score:.1f}%"
            )
        
        return matched_jobs
    
    def export_to_sheets(self, jobs: List, sheet_name: str = "Sheet1") -> bool:
        """Export matched jobs to Google Sheets"""
        if not jobs:
            self.logger.warning("No jobs to export")
            return False
        
        try:
            # Create headers
            self.sheets_service.create_headers(sheet_name)
            
            # Append jobs
            self.sheets_service.append_jobs(jobs, f"{sheet_name}!A2")
            self.logger.info(f"Successfully exported {len(jobs)} jobs to Google Sheets")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting to sheets: {e}")
            return False
    
    def save_results_locally(self, jobs: List, output_path: str = "results.json") -> bool:
        """Save matched jobs to a local JSON file"""
        try:
            jobs_data = []
            for job in jobs:
                jobs_data.append({
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "link": job.link,
                    "description": job.description,
                    "salary": job.salary,
                    "job_type": job.job_type,
                    "source": job.source,
                    "match_score": job.match_score,
                    "matched_skills": job.matched_skills,
                    "missing_skills": job.missing_skills,
                    "scraped_at": str(job.scraped_at)
                })
            
            with open(output_path, 'w') as f:
                json.dump(jobs_data, f, indent=2)
            
            self.logger.info(f"Results saved to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            return False
    
    async def run_full_pipeline(
        self,
        search_query: str,
        location: str = "",
        pages: int = 3,
        sources: Optional[List[str]] = None,
        export_sheets: bool = True,
        save_local: bool = True
    ) -> None:
        """
        Run the complete job scraping and matching pipeline.
        
        Args:
            search_query: Job search query
            location: Geographic location for search
            pages: Number of pages to scrape
            sources: Job sources to scrape
            export_sheets: Whether to export results to Google Sheets
            save_local: Whether to save results locally
        """
        # Step 1: Scrape jobs
        await self.scrape_jobs_async(search_query, location, pages, sources)
        
        # Step 2: Match and filter jobs
        matched_jobs = self.match_and_filter_jobs()
        
        if not matched_jobs:
            self.logger.warning("No matching jobs found")
            return
        
        # Step 3: Export results
        if export_sheets:
            self.export_to_sheets(matched_jobs)
        
        if save_local:
            self.save_results_locally(matched_jobs)
        
        self.logger.info("Pipeline completed successfully")


async def main():
    """Main entry point"""
    try:
        # Initialize application
        app = JobScraperApplication(
            resume_path=Config.RESUME_FILE_PATH,
            preferences_path="preferences.json" if Path("preferences.json").exists() else None
        )
        
        # Run the full pipeline
        await app.run_full_pipeline(
            search_query="Python Developer",
            location="Remote",
            pages=2,
            sources=["indeed"],
            export_sheets=False,  # Set to True if Google Sheets is configured
            save_local=True
        )
    
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Example: Create sample preferences file if it doesn't exist
    if not Path("preferences.json").exists():
        sample_prefs = {
            "target_titles": ["Python Developer", "Backend Engineer", "Full Stack Developer"],
            "required_skills": ["Python"],
            "nice_to_have_skills": ["Django", "FastAPI", "PostgreSQL", "Docker"],
            "min_salary": 80000,
            "max_salary": 200000,
            "locations": ["Remote", "San Francisco", "New York"],
            "remote_preference": "any",
            "job_types": ["Full-time"],
            "min_match_score": 50.0
        }
        with open("preferences.json", "w") as f:
            json.dump(sample_prefs, f, indent=2)
        logger.info("Created sample preferences.json file")
    
    # Run the main application
    asyncio.run(main())