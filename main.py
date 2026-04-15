# main.py
import asyncio, smtplib, os, logging
from email.mime.text import MIMEText
from datetime import datetime
from scraper import run_all_scrapers
from scorer import filter_and_score, deduplicate
from sheets_logger import get_sheet, get_seen_ids, append_jobs, update_status
from cover_letter import generate_all_letters
from applier import apply_to_jobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_pipeline():
    print("=== Zain Job Automation Pipeline ===")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    try:
        # 1. Load Google Sheet and seen job IDs
        logger.info("[1] Loading Google Sheets...")
        ws = get_sheet()
        seen_ids = get_seen_ids(ws)
        print(f"[1] Loaded sheet. {len(seen_ids)} jobs already tracked.")

        # 2. Scrape all platforms
        print("[2] Scraping job platforms...")
        logger.info("[2] Starting scrapers...")
        raw_jobs = run_all_scrapers()
        print(f"    Scraped {len(raw_jobs)} raw jobs.")
        
        if not raw_jobs:
            print("No jobs scraped today. Exiting.")
            return

        # 3. Deduplicate
        print("[3] Deduplicating...")
        new_jobs = deduplicate(raw_jobs, seen_ids)
        print(f"    {len(new_jobs)} new jobs after dedup.")

        if not new_jobs:
            print("No new jobs found. Exiting.")
            return

        # 4. Score and filter
        print("[4] Scoring and filtering...")
        qualified = filter_and_score(new_jobs, threshold=60)
        auto_apply = [j for j in qualified if j["match_score"] >= 70]
        print(f"    {len(qualified)} qualified (score ≥ 60) · {len(auto_apply)} for auto-apply (score ≥ 70)")

        # 5. Generate cover letters for auto-apply jobs
        print("[5] Generating cover letters...")
        logger.info("[5] Generating cover letters for auto-apply jobs...")
        letters = await generate_all_letters(auto_apply)
        logger.info(f"    Generated {len([l for l in letters.values() if l])} cover letters")

        # 6. Log all qualified jobs to Sheets
        print("[6] Logging to Google Sheets...")
        logger.info("[6] Appending to Google Sheets...")
        append_jobs(ws, qualified, letters)

        # 7. Auto-apply
        applied_count = 0
        print("[7] Auto-applying...")
        logger.info("[7] Starting auto-apply process...")
        
        apply_results = await apply_to_jobs(auto_apply, letters)
        
        for job in auto_apply:
            job_id = job["job_id"]
            success = apply_results.get(job_id, False)
            status = "Applied" if success else "Manual needed"
            update_status(ws, job_id, status, datetime.now().strftime("%Y-%m-%d %H:%M"))
            if success:
                applied_count += 1
                logger.info(f"    ✓ Applied to {job['title']} @ {job['company']}")
            else:
                logger.warning(f"    ✗ Manual apply needed for {job['title']} @ {job['company']}")

        # 8. Send digest email (only if applications succeeded)
        if applied_count > 0:
            send_digest(len(qualified), applied_count, auto_apply[:5])
        
        print(f"\n=== Done. {len(qualified)} logged · {applied_count} applied ===")
        logger.info(f"Pipeline complete: {len(qualified)} logged, {applied_count} applied")

    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        print(f"ERROR: {e}")
        raise

async def attempt_apply(job: dict, cover_letter: str) -> bool:
    """
    Deprecated: Use applier.apply_to_job instead.
    Kept for backward compatibility.
    """
    from applier import JobApplier
    applier = JobApplier()
    return await applier.apply_to_job(job, cover_letter)

def send_digest(total: int, applied: int, top_jobs: list[dict]):
    """
    Send email digest of daily job automation results.
    Only sent if auto-apply succeeded.
    """
    gmail_user = os.environ.get("YOUR_GMAIL", "")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD", "")
    
    if not gmail_user or not gmail_pass:
        logger.warning("Email credentials not configured. Skipping digest.")
        return
    
    body = f"""Daily Job Automation Digest — {datetime.now().strftime('%Y-%m-%d')}

✓ Jobs logged to Sheets: {total}
✓ Auto-applied: {applied}

Top matches today:
"""
    
    for i, j in enumerate(top_jobs, 1):
        salary = j.get('salary', 'N/A')
        if salary and not str(salary).startswith('$'):
            salary = f"${salary}"
        
        body += f"\n{i}. [{j['match_score']}/100] {j['title']} @ {j['company']}\n"
        body += f"   Salary: {salary}\n"
        body += f"   {j['url']}\n"

    body += f"\nView full tracker: https://docs.google.com/spreadsheets/d/{os.environ.get('SHEET_ID', 'YOUR_SHEET_ID')}\n"
    body += f"\n---\nThis is an automated message from your Job Bot."
    
    msg = MIMEText(body)
    msg["Subject"] = f"🤖 Job Bot Digest — {total} jobs, {applied} applied"
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(gmail_user, gmail_pass)
            s.sendmail(gmail_user, gmail_user, msg.as_string())
        logger.info("[8] Digest email sent.")
        print("[8] Digest email sent.")
    except Exception as e:
        logger.error(f"[8] Email failed: {e}")
        print(f"[8] Email failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_pipeline())