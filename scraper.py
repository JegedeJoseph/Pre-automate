# scraper.py
import asyncio, json, re, logging
from datetime import date
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TITLES = [
    "Senior Software Engineer", "Software Engineer",
    "AI Engineer", "Machine Learning Engineer",
    "Backend Engineer", "Full Stack Engineer"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

async def scrape_remoteok() -> list[dict]:
    """
    Scrape RemoteOK.com for remote engineering jobs.
    RemoteOK has dynamic content loaded with JavaScript.
    """
    jobs = []
    max_retries = 3
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(extra_http_headers=HEADERS)
        page = await context.new_page()
        
        search_terms = ["software-engineer", "ai-engineer", "backend", "fullstack"]
        
        for term in search_terms:
            for attempt in range(max_retries):
                try:
                    url = f"https://remoteok.com/remote-{term}-jobs"
                    await page.goto(url, wait_until="networkidle", timeout=15000)
                    await page.wait_for_timeout(2000)  # Let JS render
                    
                    # Find job rows - RemoteOK uses <tr> elements
                    rows = await page.query_selector_all("tr.job")
                    logger.info(f"RemoteOK ({term}): Found {len(rows)} jobs on attempt {attempt+1}")
                    
                    for row in rows:
                        try:
                            # Job title is usually in a td > a > b or h2
                            title_el = await row.query_selector("td:nth-child(2) a, .font-bold, h2")
                            company_el = await row.query_selector("td:nth-child(3), .company-name")
                            link_el = await row.query_selector("a[href*='/jobs/']")
                            salary_el = await row.query_selector(".salary, td:contains('$')")
                            
                            title_text = await title_el.inner_text() if title_el else ""
                            company_text = await company_el.inner_text() if company_el else ""
                            href = await link_el.get_attribute("href") if link_el else ""
                            salary_text = await salary_el.inner_text() if salary_el else ""
                            
                            # Get job description from page detail (optional light scrape)
                            description = await row.inner_text() if row else ""
                            
                            if title_text and href:
                                jobs.append({
                                    "platform": "RemoteOK",
                                    "title": title_text.strip(),
                                    "company": company_text.strip() if company_text else "Unknown",
                                    "location": "Remote",
                                    "salary": salary_text.strip(),
                                    "description": description[:500],  # First 500 chars
                                    "url": f"https://remoteok.com{href}" if not href.startswith("http") else href,
                                    "apply_url": f"https://remoteok.com{href}" if not href.startswith("http") else href,
                                    "job_id": f"remoteok_{re.sub(r'[^a-z0-9]', '_', href.lower())}",
                                    "date_scraped": str(date.today())
                                })
                        except Exception as e:
                            logger.debug(f"Error parsing RemoteOK job row: {e}")
                            continue
                    
                    if len(rows) > 0:
                        break  # Success, move to next term
                        
                except Exception as e:
                    logger.warning(f"RemoteOK attempt {attempt+1} failed for {term}: {e}")
                    if attempt == max_retries - 1:
                        logger.error(f"RemoteOK final failure for {term}")
                    await page.wait_for_timeout(1000)
        
        await browser.close()
    
    logger.info(f"RemoteOK: Scraped total {len(jobs)} jobs")
    return jobs

async def scrape_weworkremotely() -> list[dict]:
    """
    Scrape WeWorkRemotely.com for remote engineering jobs.
    """
    jobs = []
    max_retries = 3
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(extra_http_headers=HEADERS)
        page = await context.new_page()
        
        categories = [
            "remote-full-stack-programming-jobs",
            "remote-back-end-programming-jobs",
            "remote-front-end-programming-jobs"
        ]
        
        for cat in categories:
            for attempt in range(max_retries):
                try:
                    url = f"https://weworkremotely.com/categories/{cat}"
                    await page.goto(url, wait_until="networkidle", timeout=15000)
                    await page.wait_for_timeout(1500)
                    
                    # WeWorkRemotely uses li.feature elements
                    listings = await page.query_selector_all("li.feature")
                    logger.info(f"WeWorkRemotely ({cat}): Found {len(listings)} jobs on attempt {attempt+1}")
                    
                    for item in listings:
                        try:
                            # Extract job data
                            title_el = await item.query_selector("span.title, a.posting-title")
                            company_el = await item.query_selector("span.company, a.company")
                            link_el = await item.query_selector("a")
                            
                            title_text = await title_el.inner_text() if title_el else ""
                            company_text = await company_el.inner_text() if company_el else ""
                            href = await link_el.get_attribute("href") if link_el else ""
                            description = await item.inner_text() if item else ""
                            
                            if title_text and href:
                                jobs.append({
                                    "platform": "WeWorkRemotely",
                                    "title": title_text.strip(),
                                    "company": company_text.strip() if company_text else "Unknown",
                                    "location": "Remote",
                                    "salary": "",
                                    "description": description[:500],
                                    "url": f"https://weworkremotely.com{href}" if not href.startswith("http") else href,
                                    "apply_url": f"https://weworkremotely.com{href}" if not href.startswith("http") else href,
                                    "job_id": f"wwr_{re.sub(r'[^a-z0-9]', '_', href.lower())}",
                                    "date_scraped": str(date.today())
                                })
                        except Exception as e:
                            logger.debug(f"Error parsing WeWorkRemotely job: {e}")
                            continue
                    
                    if len(listings) > 0:
                        break
                        
                except Exception as e:
                    logger.warning(f"WeWorkRemotely attempt {attempt+1} failed for {cat}: {e}")
                    if attempt == max_retries - 1:
                        logger.error(f"WeWorkRemotely final failure for {cat}")
                    await page.wait_for_timeout(1000)
        
        await browser.close()
    
    logger.info(f"WeWorkRemotely: Scraped total {len(jobs)} jobs")
    return jobs

async def scrape_simplify() -> list[dict]:
    """
    Scrape Simplify.jobs public API for remote engineering jobs.
    Simplify.jobs exposes a public API endpoint for job search - no auth needed.
    """
    import httpx
    jobs = []
    queries = [
        "AI Engineer", 
        "Senior Software Engineer", 
        "Machine Learning Engineer",
        "Backend Engineer",
        "Full Stack Engineer"
    ]
    
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=20) as client:
            for q in queries:
                try:
                    # Query Simplify.jobs public API
                    r = await client.get(
                        "https://simplify.jobs/api/v2/jobs",
                        params={
                            "query": q, 
                            "remote": "true", 
                            "page": 1, 
                            "limit": 50,
                            "location": "US,CA"  # USA & Canada
                        }
                    )
                    r.raise_for_status()
                    data = r.json()
                    
                    for job in data.get("jobs", []):
                        # Parse salary range
                        salary_min = job.get("salary", {}).get("min", 0) if isinstance(job.get("salary"), dict) else None
                        salary_str = ""
                        if salary_min:
                            salary_str = f"${salary_min:,}"
                        elif job.get("salary"):
                            salary_str = str(job.get("salary"))
                        
                        job_data = {
                            "platform": "Simplify",
                            "title": job.get("title", ""),
                            "company": job.get("company", {}).get("name", "") if isinstance(job.get("company"), dict) else job.get("company", ""),
                            "location": job.get("location", "Remote"),
                            "salary": salary_str,
                            "description": job.get("description", "")[:500],
                            "url": job.get("url", ""),
                            "apply_url": job.get("apply_url", job.get("url", "")),
                            "job_id": f"simplify_{job.get('id','')}",
                            "date_scraped": str(date.today())
                        }
                        
                        if job_data["title"] and job_data["url"]:
                            jobs.append(job_data)
                    
                    logger.info(f"Simplify ({q}): Found {len(data.get('jobs', []))} jobs")
                    await asyncio.sleep(0.5)  # Be respectful to API
                    
                except httpx.HTTPStatusError as e:
                    logger.warning(f"Simplify API error for '{q}': {e.status_code}")
                except Exception as e:
                    logger.warning(f"Simplify query '{q}' failed: {e}")
                    continue
                    
    except Exception as e:
        logger.error(f"Simplify scraper failed: {e}")
    
    logger.info(f"Simplify: Scraped total {len(jobs)} jobs")
    return jobs

async def scrape_linkedin() -> list[dict]:
    """
    LinkedIn scraper - placeholder. Requires authentication.
    Will be implemented once credentials are available.
    """
    logger.info("LinkedIn scraper: Awaiting credentials setup")
    return []

async def scrape_indeed() -> list[dict]:
    """
    Indeed scraper - placeholder. Requires special handling.
    Will be implemented once approved.
    """
    logger.info("Indeed scraper: Awaiting implementation")
    return []

async def scrape_glassdoor() -> list[dict]:
    """
    Glassdoor scraper - placeholder.
    Will be implemented once approved.
    """
    logger.info("Glassdoor scraper: Awaiting implementation")
    return []

async def scrape_wellfound() -> list[dict]:
    """
    Wellfound (formerly AngelList Talent) scraper.
    Wellfound has a public API for startup jobs.
    """
    import httpx
    jobs = []
    
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=20) as client:
            # Wellfound API for startup jobs
            keywords = ["engineer", "ai", "ml", "backend"]
            
            for keyword in keywords:
                try:
                    # Note: Wellfound may require API key - adjust if needed
                    r = await client.get(
                        "https://api.wellfound.com/jobs",
                        params={
                            "keywords": keyword,
                            "remote_ok": "true",
                            "locations": "remote",
                            "limit": 50
                        },
                        timeout=15
                    )
                    r.raise_for_status()
                    data = r.json()
                    
                    for job in data.get("jobs", []):
                        jobs.append({
                            "platform": "Wellfound",
                            "title": job.get("title", ""),
                            "company": job.get("company", {}).get("name", "") if isinstance(job.get("company"), dict) else job.get("company", ""),
                            "location": "Remote",
                            "salary": job.get("salary_min", ""),
                            "description": job.get("description", "")[:500],
                            "url": job.get("url", ""),
                            "apply_url": job.get("apply_url", job.get("url", "")),
                            "job_id": f"wellfound_{job.get('id','')}",
                            "date_scraped": str(date.today())
                        })
                    
                    logger.info(f"Wellfound ({keyword}): Found {len(data.get('jobs', []))} jobs")
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.debug(f"Wellfound keyword '{keyword}' failed: {e}")
                    continue
                    
    except Exception as e:
        logger.warning(f"Wellfound scraper failed: {e}")
    
    logger.info(f"Wellfound: Scraped total {len(jobs)} jobs")
    return jobs

def run_all_scrapers() -> list[dict]:
    """
    Run all scrapers concurrently and aggregate results.
    Focus: RemoteOK, WeWorkRemotely, Simplify (free/public platforms)
    """
    loop = asyncio.get_event_loop()
    tasks = [
        scrape_remoteok(),
        scrape_weworkremotely(),
        scrape_simplify(),
        # Placeholders for future implementation:
        # scrape_linkedin(),        # Awaiting credentials
        # scrape_indeed(),          # Awaiting approval
        # scrape_glassdoor(),       # Awaiting approval
        # scrape_wellfound(),       # Optional - requires API key
    ]
    
    try:
        results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    except RuntimeError:
        # Handle event loop issues on some systems
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    
    all_jobs = []
    for r in results:
        if isinstance(r, list):
            all_jobs.extend(r)
        elif isinstance(r, Exception):
            logger.error(f"Scraper failed: {r}")
    
    logger.info(f"Total jobs scraped: {len(all_jobs)}")
    return all_jobs

if __name__ == "__main__":
    jobs = run_all_scrapers()
    print(json.dumps(jobs, indent=2))
    print(f"\nTotal scraped: {len(jobs)}")