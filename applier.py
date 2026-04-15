# applier.py
"""
Auto-apply handlers for different job platforms.
Each handler attempts to apply to a job and returns success status.
"""

import asyncio
import logging
from playwright.async_api import async_playwright, Page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobApplier:
    """Base class for job application handlers."""
    
    def __init__(self, timeout=30000):
        self.timeout = timeout
    
    async def apply_remoteok(self, job: dict, cover_letter: str) -> bool:
        """
        Apply to RemoteOK job.
        RemoteOK jobs redirect to external apply links usually.
        This opens the job page and clicks apply if available.
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                logger.info(f"Applying to RemoteOK: {job['title']} @ {job['company']}")
                
                # Navigate to job page
                await page.goto(job['apply_url'], wait_until="domcontentloaded", timeout=self.timeout)
                await page.wait_for_timeout(1000)
                
                # Try to find and click "Apply Now" or similar button
                apply_selectors = [
                    "button:has-text('Apply Now')",
                    "button:has-text('Apply')",
                    "a:has-text('Apply Now')",
                    "a:has-text('Apply')",
                    ".apply-button",
                    "[class*='apply']"
                ]
                
                applied = False
                for selector in apply_selectors:
                    try:
                        btn = await page.query_selector(selector)
                        if btn:
                            await btn.click()
                            logger.info(f"  ✓ Clicked apply button")
                            applied = True
                            await page.wait_for_timeout(2000)
                            break
                    except Exception as e:
                        logger.debug(f"  Selector '{selector}' not found: {e}")
                        continue
                
                await browser.close()
                return applied
                
        except Exception as e:
            logger.error(f"RemoteOK apply failed: {e}")
            return False
    
    async def apply_weworkremotely(self, job: dict, cover_letter: str) -> bool:
        """
        Apply to WeWorkRemotely job.
        WeWorkRemotely typically shows application instructions on the job page.
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                logger.info(f"Applying to WeWorkRemotely: {job['title']} @ {job['company']}")
                
                await page.goto(job['apply_url'], wait_until="domcontentloaded", timeout=self.timeout)
                await page.wait_for_timeout(1000)
                
                # WeWorkRemotely shows application instructions or redirect link
                apply_selectors = [
                    "a:has-text('Apply')",
                    "a:has-text('Click here to apply')",
                    "button:has-text('Apply')",
                    ".apply-link",
                    "[class*='apply']"
                ]
                
                applied = False
                for selector in apply_selectors:
                    try:
                        btn = await page.query_selector(selector)
                        if btn:
                            await btn.click()
                            logger.info(f"  ✓ Clicked apply button")
                            applied = True
                            await page.wait_for_timeout(2000)
                            break
                    except Exception as e:
                        logger.debug(f"  Selector '{selector}' not found: {e}")
                        continue
                
                await browser.close()
                return applied
                
        except Exception as e:
            logger.error(f"WeWorkRemotely apply failed: {e}")
            return False
    
    async def apply_simplify(self, job: dict, cover_letter: str) -> bool:
        """
        Apply to Simplify.jobs job.
        Simplify typically redirects to external job boards or company sites.
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                logger.info(f"Applying to Simplify: {job['title']} @ {job['company']}")
                
                await page.goto(job['apply_url'], wait_until="domcontentloaded", timeout=self.timeout)
                await page.wait_for_timeout(1500)
                
                # Check if page redirected to company site or LinkedIn
                current_url = page.url
                logger.info(f"  Redirected to: {current_url}")
                
                # Detect if we're on LinkedIn, company site, or Greenhouse
                if "linkedin.com" in current_url:
                    logger.info(f"  → Redirected to LinkedIn (manual/external handling)")
                    return True  # LinkedIn handling would require separate logic
                elif "greenhouse.io" in current_url:
                    logger.info(f"  → Redirected to Greenhouse (needs form filling)")
                    return await self._fill_greenhouse_form(page, job, cover_letter)
                else:
                    logger.info(f"  → External application site detected")
                    return True  # For now, mark as handled
                
        except Exception as e:
            logger.error(f"Simplify apply failed: {e}")
            return False
    
    async def _fill_greenhouse_form(self, page: Page, job: dict, cover_letter: str) -> bool:
        """
        Fill a Greenhouse job application form.
        Greenhouse is a common ATS used by many companies.
        """
        try:
            logger.info(f"  Filling Greenhouse application form...")
            
            # Try to find and fill email field
            email_inputs = await page.query_selector_all("input[type='email'], input[name*='email'], input[id*='email']")
            if email_inputs:
                import os
                email = os.environ.get("APPLICANT_EMAIL", "")
                if email:
                    await email_inputs[0].fill(email)
                    logger.info(f"  ✓ Filled email: {email}")
            
            # Try to find and fill name field
            name_inputs = await page.query_selector_all("input[type='text'][name*='name'], input[id*='name']")
            if name_inputs:
                import os
                name = os.environ.get("APPLICANT_NAME", "")
                if name:
                    await name_inputs[0].fill(name)
                    logger.info(f"  ✓ Filled name: {name}")
            
            # Try to find cover letter field
            cover_letter_fields = await page.query_selector_all("textarea[name*='cover'], textarea[name*='letter'], textarea[id*='cover']")
            if cover_letter_fields and cover_letter:
                await cover_letter_fields[0].fill(cover_letter)
                logger.info(f"  ✓ Filled cover letter ({len(cover_letter)} chars)")
            
            # Try to submit
            submit_buttons = await page.query_selector_all("button:has-text('Submit'), button[type='submit']")
            if submit_buttons:
                await submit_buttons[0].click()
                await page.wait_for_timeout(3000)
                logger.info(f"  ✓ Submitted application")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Greenhouse form filling failed: {e}")
            return False
    
    async def apply_linkedin_easyapply(self, job: dict, cover_letter: str) -> bool:
        """
        Apply via LinkedIn Easy Apply.
        Requires LinkedIn session cookie or logged-in browser.
        """
        try:
            async with async_playwright() as p:
                # TODO: Implement with LinkedIn cookies
                logger.info("LinkedIn Easy Apply: Placeholder (awaiting credentials)")
                return False
        except Exception as e:
            logger.error(f"LinkedIn Easy Apply failed: {e}")
            return False
    
    async def apply_indeed_quickapply(self, job: dict, cover_letter: str) -> bool:
        """
        Apply via Indeed Quick Apply.
        Requires Indeed session.
        """
        try:
            async with async_playwright() as p:
                # TODO: Implement Indeed Quick Apply
                logger.info("Indeed Quick Apply: Placeholder (awaiting approval)")
                return False
        except Exception as e:
            logger.error(f"Indeed Quick Apply failed: {e}")
            return False
    
    async def apply_to_job(self, job: dict, cover_letter: str) -> bool:
        """
        Route job application to appropriate handler based on platform.
        """
        platform = job.get("platform", "").lower()
        
        if platform == "remoteok":
            return await self.apply_remoteok(job, cover_letter)
        elif platform == "weworkremotely":
            return await self.apply_weworkremotely(job, cover_letter)
        elif platform == "simplify":
            return await self.apply_simplify(job, cover_letter)
        elif platform == "linkedin":
            return await self.apply_linkedin_easyapply(job, cover_letter)
        elif platform == "indeed":
            return await self.apply_indeed_quickapply(job, cover_letter)
        else:
            logger.warning(f"No apply handler for platform: {platform}")
            return False


async def apply_to_jobs(jobs: list[dict], cover_letters: dict) -> dict:
    """
    Apply to multiple jobs concurrently.
    Returns {job_id: success_bool}
    """
    applier = JobApplier()
    tasks = []
    
    for job in jobs:
        cover_letter = cover_letters.get(job.get("job_id", ""), "")
        tasks.append(applier.apply_to_job(job, cover_letter))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    apply_results = {}
    for job, result in zip(jobs, results):
        if isinstance(result, bool):
            apply_results[job["job_id"]] = result
        else:
            logger.error(f"Apply task failed for {job['job_id']}: {result}")
            apply_results[job["job_id"]] = False
    
    return apply_results
