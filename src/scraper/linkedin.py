import asyncio
from typing import List
from playwright.async_api import async_playwright, Page
from src.models import JobListing
from src.utils import setup_logger, Config

logger = setup_logger(__name__)

class LinkedInScraper:
    """Scraper for LinkedIn job listings"""
    
    BASE_URL = "https://www.linkedin.com/jobs/search"
    
    def __init__(self):
        self.logger = logger
    
    async def scrape(self, search_query: str, location: str = "", pages: int = 3) -> List[JobListing]:
        """Scrape jobs from LinkedIn"""
        jobs = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=Config.HEADLESS_BROWSER)
            page = await browser.new_page()
            
            for page_num in range(pages):
                try:
                    url = self._build_url(search_query, location, page_num)
                    self.logger.info(f"Scraping LinkedIn page {page_num + 1}: {url}")
                    
                    await page.goto(url, wait_until='networkidle', timeout=Config.BROWSER_TIMEOUT)
                    await page.wait_for_timeout(3000)  # LinkedIn needs more time
                    
                    # Get job listings
                    job_cards = await page.query_selector_all('ul.jobs-search__results-list > li')
                    self.logger.debug(f"Found {len(job_cards)} job cards on page {page_num + 1}")
                    
                    for job_card in job_cards:
                        job = await self._extract_job_info(job_card, page)
                        if job:
                            jobs.append(job)
                
                except Exception as e:
                    self.logger.error(f"Error scraping LinkedIn page {page_num + 1}: {e}")
                    continue
            
            await browser.close()
        
        self.logger.info(f"Scraped {len(jobs)} jobs from LinkedIn")
        return jobs
    
    def _build_url(self, search_query: str, location: str, page_num: int) -> str:
        """Build LinkedIn search URL"""
        url = f"{self.BASE_URL}/?keywords={search_query.replace(' ', '%20')}"
        if location:
            url += f"&location={location.replace(' ', '%20')}"
        if page_num > 0:
            url += f"&start={page_num * 25}"
        return url
    
    async def _extract_job_info(self, job_card, page: Page) -> JobListing:
        """Extract job information from a card"""
        try:
            title = await job_card.evaluate('el => el.querySelector(".base-search-card__title")?.textContent || ""')
            company = await job_card.evaluate('el => el.querySelector(".base-search-card__subtitle")?.textContent || ""')
            location = await job_card.evaluate('el => el.querySelector(".job-search-card__location")?.textContent || ""')
            link = await job_card.evaluate('el => el.querySelector("a")?.href || ""')
            
            # Create job listing
            job = JobListing(
                title=title.strip(),
                company=company.strip(),
                location=location.strip(),
                link=link.strip(),
                source="LinkedIn"
            )
            
            return job if job.title and job.company else None
        
        except Exception as e:
            self.logger.debug(f"Error extracting job info: {e}")
            return None
