# scraper.py
import asyncio, json, re
from datetime import date
from playwright.async_api import async_playwright

TITLES = [
    "Senior Software Engineer", "Software Engineer",
    "AI Engineer", "Machine Learning Engineer",
    "Backend Engineer", "Full Stack Engineer"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
}

async def scrape_remoteok() -> list[dict]:
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for title in ["software-engineer", "ai-engineer", "machine-learning", "backend", "fullstack"]:
            await page.goto(f"https://remoteok.com/remote-{title}-jobs", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            rows = await page.query_selector_all("tr.job")
            for row in rows:
                try:
                    title_el = await row.query_selector("h2")
                    company_el = await row.query_selector("h3")
                    link_el = await row.query_selector("a.preventLink")
                    salary_el = await row.query_selector(".salary")
                    title_text = await title_el.inner_text() if title_el else ""
                    company_text = await company_el.inner_text() if company_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""
                    salary_text = await salary_el.inner_text() if salary_el else ""
                    jobs.append({
                        "platform": "RemoteOK",
                        "title": title_text.strip(),
                        "company": company_text.strip(),
                        "location": "Remote",
                        "salary": salary_text.strip(),
                        "url": f"https://remoteok.com{href}",
                        "apply_url": f"https://remoteok.com{href}",
                        "job_id": f"remoteok_{href.replace('/','_')}",
                        "date_scraped": str(date.today())
                    })
                except Exception:
                    continue
        await browser.close()
    return jobs

async def scrape_weworkremotely() -> list[dict]:
    jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        categories = ["remote-full-stack-programming-jobs", "remote-back-end-programming-jobs"]
        for cat in categories:
            await page.goto(f"https://weworkremotely.com/categories/{cat}", wait_until="domcontentloaded")
            await page.wait_for_timeout(1500)
            listings = await page.query_selector_all("li.feature")
            for item in listings:
                try:
                    title_el = await item.query_selector("span.title")
                    company_el = await item.query_selector("span.company")
                    link_el = await item.query_selector("a")
                    title_text = await title_el.inner_text() if title_el else ""
                    company_text = await company_el.inner_text() if company_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""
                    jobs.append({
                        "platform": "WeWorkRemotely",
                        "title": title_text.strip(),
                        "company": company_text.strip(),
                        "location": "Remote",
                        "salary": "",
                        "url": f"https://weworkremotely.com{href}",
                        "apply_url": f"https://weworkremotely.com{href}",
                        "job_id": f"wwr_{href.replace('/','_')}",
                        "date_scraped": str(date.today())
                    })
                except Exception:
                    continue
        await browser.close()
    return jobs

async def scrape_simplify() -> list[dict]:
    """
    Simplify.jobs exposes a public API endpoint for job search.
    """
    import httpx
    jobs = []
    queries = ["AI Engineer", "Senior Software Engineer", "Machine Learning Engineer"]
    async with httpx.AsyncClient(headers=HEADERS, timeout=15) as client:
        for q in queries:
            try:
                r = await client.get(
                    "https://simplify.jobs/api/v2/jobs",
                    params={"query": q, "remote": "true", "page": 1, "limit": 30}
                )
                data = r.json()
                for job in data.get("jobs", []):
                    jobs.append({
                        "platform": "Simplify",
                        "title": job.get("title", ""),
                        "company": job.get("company", {}).get("name", ""),
                        "location": "Remote",
                        "salary": job.get("salary", ""),
                        "url": job.get("url", ""),
                        "apply_url": job.get("apply_url", job.get("url", "")),
                        "job_id": f"simplify_{job.get('id','')}",
                        "date_scraped": str(date.today())
                    })
            except Exception:
                continue
    return jobs

def run_all_scrapers() -> list[dict]:
    loop = asyncio.get_event_loop()
    tasks = [
        scrape_remoteok(),
        scrape_weworkremotely(),
        scrape_simplify()
    ]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    all_jobs = []
    for r in results:
        all_jobs.extend(r)
    return all_jobs

if __name__ == "__main__":
    jobs = run_all_scrapers()
    print(json.dumps(jobs, indent=2))
    print(f"\nTotal scraped: {len(jobs)}")