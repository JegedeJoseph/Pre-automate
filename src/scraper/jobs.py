"""Orchestrates job scraping from multiple sources."""
import asyncio
from typing import List, Optional
from src.models import JobListing
from src.utils import setup_logger

logger = setup_logger(__name__)


class JobScraper:
    """Orchestrates job scraping from multiple sources"""
    
    def __init__(self):
        """Initialize the job scraper"""
        self.logger = logger
        self._scrapers = self._initialize_scrapers()
    
    def _initialize_scrapers(self):
        """Initialize all available scrapers"""
        scrapers = {}
        
        try:
            from .indeed import IndeedScraper
            scrapers['indeed'] = IndeedScraper()
            self.logger.info("Indeed scraper initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize Indeed scraper: {e}")
        
        try:
            from .linkedin import LinkedInScraper
            scrapers['linkedin'] = LinkedInScraper()
            self.logger.info("LinkedIn scraper initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize LinkedIn scraper: {e}")
        
        try:
            from .glassdoor import GlassdoorScraper
            scrapers['glassdoor'] = GlassdoorScraper()
            self.logger.info("Glassdoor scraper initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize Glassdoor scraper: {e}")
        
        return scrapers
    
    async def scrape_all(
        self,
        search_query: str,
        location: str = "",
        pages: int = 3,
        sources: Optional[List[str]] = None
    ) -> List[JobListing]:
        """
        Scrape jobs from multiple sources.
        
        Args:
            search_query: Search query for jobs
            location: Location filter
            pages: Number of pages to scrape per source
            sources: List of sources to scrape (indeed, linkedin, glassdoor)
        
        Returns:
            List of JobListing objects
        """
        if sources is None:
            sources = ["indeed"]
        
        # Filter to only available scrapers
        available_sources = [s for s in sources if s in self._scrapers]
        
        if not available_sources:
            self.logger.error(f"No available scrapers for sources: {sources}")
            return []
        
        self.logger.info(f"Scraping from sources: {available_sources}")
        
        # Create tasks for each source
        tasks = []
        for source in available_sources:
            scraper = self._scrapers[source]
            task = scraper.scrape(
                search_query=search_query,
                location=location,
                pages=pages
            )
            tasks.append(task)
        
        # Run all scrapers concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results and handle exceptions
        all_jobs = []
        for source, result in zip(available_sources, results):
            if isinstance(result, Exception):
                self.logger.error(f"Error scraping {source}: {result}")
            elif isinstance(result, list):
                all_jobs.extend(result)
                self.logger.info(f"Scraped {len(result)} jobs from {source}")
        
        # Remove duplicates based on link
        unique_jobs = {}
        for job in all_jobs:
            if job.link not in unique_jobs:
                unique_jobs[job.link] = job
        
        final_jobs = list(unique_jobs.values())
        self.logger.info(f"Total unique jobs after deduplication: {len(final_jobs)}")
        
        return final_jobs
