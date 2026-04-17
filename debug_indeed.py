"""
Debug script to inspect Indeed page structure
"""
import asyncio
from playwright.async_api import async_playwright

async def debug_indeed():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://www.indeed.com/jobs?q=Python+Developer&l=Remote"
        print(f"Navigating to: {url}")
        
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Get page content
        content = await page.content()
        
        # Look for job markers
        if 'data-job-id' in content:
            print("✓ Found 'data-job-id' in page")
        else:
            print("✗ 'data-job-id' not found")
        
        if 'job-search-results' in content:
            print("✓ Found 'job-search-results' in page")
        else:
            print("✗ 'job-search-results' not found")
        
        # Count some markers
        job_id_count = content.count('data-job-id')
        print(f"Found {job_id_count} instances of 'data-job-id'")
        
        # Try different selectors
        selectors = [
            'div[data-job-id]',
            '.jobs-search-results li',
            'div[role="region"]',
            'div.job_seen_beacon',
            '.resultslist li'
        ]
        
        print("\nTrying selectors:")
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                print(f"  {selector}: {len(elements)} found")
            except Exception as e:
                print(f"  {selector}: Error - {e}")
        
        # Save first job element for inspection
        job_elem = await page.query_selector('div[data-job-id]')
        if job_elem:
            print("\nFirst job element HTML:")
            html = await job_elem.inner_html()
            print(html[:500])  # First 500 chars
        else:
            print("\nNo job element found with 'div[data-job-id]'")
            
            # Try to find any job-like element
            li_elem = await page.query_selector('.jobs-search-results li')
            if li_elem:
                print("Found job in .jobs-search-results li")
                html = await li_elem.inner_html()
                print(html[:500])
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_indeed())
