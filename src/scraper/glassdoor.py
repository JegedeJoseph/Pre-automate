import asyncio
from typing import List
from playwright.async_api import async_playwright, Page
from src.models import JobListing
from src.utils import setup_logger, Config

logger = setup_logger(__name__)

class GlassdoorScraper:
    """Scraper for Glassdoor job listings"""
    
    BASE_URL = "https://www.glassdoor.com/Job/jobs.htm"
    
    def __init__(self):
        self.logger = logger
    
    async def scrape(self, search_query: str, location: str = "", pages: int = 3) -> List[JobListing]:
        """Scrape jobs from Glassdoor"""
        jobs = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=Config.HEADLESS_BROWSER)
            page = await browser.new_page()
            
            for page_num in range(pages):
                try:
                    url = self._build_url(search_query, location, page_num)
                    self.logger.info(f"Scraping Glassdoor page {page_num + 1}: {url}")
                    
                    await page.goto(url, wait_until='networkidle', timeout=Config.BROWSER_TIMEOUT)
                    await page.wait_for_timeout(2000)
                    
                    # Get job listings
                    job_cards = await page.query_selector_all('li[data-id]')
                    self.logger.debug(f"Found {len(job_cards)} job cards on page {page_num + 1}")
                    
                    for job_card in job_cards:
                        job = await self._extract_job_info(job_card, page)
                        if job:
                            jobs.append(job)
                
                except Exception as e:
                    self.logger.error(f"Error scraping Glassdoor page {page_num + 1}: {e}")
                    continue
            
            await browser.close()
        
        self.logger.info(f"Scraped {len(jobs)} jobs from Glassdoor")
        return jobs
    
    def _build_url(self, search_query: str, location: str, page_num: int) -> str:
        """Build Glassdoor search URL"""
        url = f"{self.BASE_URL}?keyword={search_query.replace(' ', '+')}"
        if location:
            url += f"&location={location.replace(' ', '+')}"
        if page_num > 0:
            url += f"&p.p={page_num + 1}"
        return url
    
    async def _extract_job_info(self, job_card, page: Page) -> JobListing:
        """Extract job information from a card"""
        try:
            title = await job_card.evaluate('el => el.querySelector(".job-search-key-match")?.textContent || el.querySelector(".jobTitle")?.textContent || ""')
            company = await job_card.evaluate('el => el.querySelector(".employer-name")?.textContent || ""')
            location = await job_card.evaluate('el => el.querySelector(".job-search-attribute-location")?.textContent || ""')
            salary = await job_card.evaluate('el => el.querySelector(".salary-estimate")?.textContent || ""')
            link = await job_card.evaluate('el => el.querySelector("a")?.href || ""')
            
            # Create job listing
            job = JobListing(
                title=title.strip(),
                company=company.strip(),
                location=location.strip(),
                salary=salary.strip() if salary else None,
                link=link.strip(),
                source="Glassdoor"
            )
            
            return job if job.title and job.company else None
        
        except Exception as e:
            self.logger.debug(f"Error extracting job info: {e}")
            return None
