import asyncio
from typing import List
from playwright.async_api import async_playwright, Page
from src.models import JobListing
from src.utils import setup_logger, Config

logger = setup_logger(__name__)

class IndeedScraper:
    """Scraper for Indeed.com job listings"""
    
    BASE_URL = "https://www.indeed.com/jobs"
    
    def __init__(self):
        self.logger = logger
    
    async def scrape(self, search_query: str, location: str = "", pages: int = 3) -> List[JobListing]:
        """Scrape jobs from Indeed"""
        jobs = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=Config.HEADLESS_BROWSER)
            page = await browser.new_page()
            
            for page_num in range(pages):
                try:
                    url = self._build_url(search_query, location, page_num)
                    self.logger.info(f"Scraping Indeed page {page_num + 1}: {url}")
                    
                    await page.goto(url, wait_until='networkidle', timeout=Config.BROWSER_TIMEOUT)
                    await page.wait_for_timeout(2000)  # Wait for JS to load
                    
                    # Get job listings
                    job_cards = await page.query_selector_all('div[data-job-id]')
                    self.logger.debug(f"Found {len(job_cards)} job cards on page {page_num + 1}")
                    
                    for job_card in job_cards:
                        job = await self._extract_job_info(job_card, page)
                        if job:
                            jobs.append(job)
                
                except Exception as e:
                    self.logger.error(f"Error scraping Indeed page {page_num + 1}: {e}")
                    continue
            
            await browser.close()
        
        self.logger.info(f"Scraped {len(jobs)} jobs from Indeed")
        return jobs
    
    def _build_url(self, search_query: str, location: str, page_num: int) -> str:
        """Build Indeed search URL"""
        url = f"{self.BASE_URL}?q={search_query.replace(' ', '+')}"
        if location:
            url += f"&l={location.replace(' ', '+')}"
        if page_num > 0:
            url += f"&start={page_num * 10}"
        return url
    
    async def _extract_job_info(self, job_card, page: Page) -> JobListing:
        """Extract job information from a card"""
        try:
            # Try multiple selectors for title
            title = ""
            for selector in [".jobTitle", "a[data-testid='job-item-title']", ".jobs-search-results__job-title"]:
                title_elem = await job_card.query_selector(selector)
                if title_elem:
                    title = await title_elem.inner_text()
                    break
            
            # If no title found, skip
            if not title:
                return None
            
            # Try multiple selectors for company
            company = ""
            for selector in ["[data-testid='company-name']", ".company", ".companyName"]:
                company_elem = await job_card.query_selector(selector)
                if company_elem:
                    company = await company_elem.inner_text()
                    break
            
            # Try multiple selectors for location
            location = ""
            for selector in ["[data-testid='job-location']", ".location", ".jobLocation"]:
                loc_elem = await job_card.query_selector(selector)
                if loc_elem:
                    location = await loc_elem.inner_text()
                    break
            
            # Get link
            link = ""
            link_elem = await job_card.query_selector("a")
            if link_elem:
                href = await link_elem.get_attribute("href")
                if href:
                    link = href if href.startswith("http") else f"https://www.indeed.com{href}"
            
            # Create job listing only if we have title and link
            if title and link:
                job = JobListing(
                    title=title.strip(),
                    company=company.strip() or "Unknown",
                    location=location.strip() or "Not specified",
                    link=link.strip(),
                    source="Indeed"
                )
                return job
            
            return None
        
        except Exception as e:
            self.logger.debug(f"Error extracting job info: {e}")
            return None
            return None
