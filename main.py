# main.py
import asyncio, smtplib, os
from email.mime.text import MIMEText
from datetime import datetime
from scraper import run_all_scrapers
from scorer import filter_and_score, deduplicate
from sheets_logger import get_sheet, get_seen_ids, append_jobs, update_status
from cover_letter import generate_all_letters

async def run_pipeline():
    print("=== Zain Job Automation Pipeline ===")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # 1. Load Google Sheet and seen job IDs
    ws = get_sheet()
    seen_ids = get_seen_ids(ws)
    print(f"[1] Loaded sheet. {len(seen_ids)} jobs already tracked.")

    # 2. Scrape all platforms
    print("[2] Scraping job platforms...")
    raw_jobs = run_all_scrapers()
    print(f"    Scraped {len(raw_jobs)} raw jobs.")

    # 3. Deduplicate
    new_jobs = deduplicate(raw_jobs, seen_ids)
    print(f"    {len(new_jobs)} new jobs after dedup.")

    # 4. Score and filter
    qualified = filter_and_score(new_jobs, threshold=60)
    auto_apply = [j for j in qualified if j["match_score"] >= 70]
    print(f"    {len(qualified)} qualified (score ≥ 60) · {len(auto_apply)} for auto-apply (score ≥ 70)")

    if not qualified:
        print("No new qualified jobs today.")
        return

    # 5. Generate cover letters for auto-apply jobs
    print("[4] Generating cover letters...")
    letters = await generate_all_letters(auto_apply)

    # 6. Log all qualified jobs to Sheets
    print("[5] Logging to Google Sheets...")
    append_jobs(ws, qualified, letters)

    # 7. Auto-apply
    applied_count = 0
    print("[6] Auto-applying...")
    for job in auto_apply:
        success = await attempt_apply(job, letters.get(job["job_id"], ""))
        status = "Applied" if success else "Manual needed"
        update_status(ws, job["job_id"], status, datetime.now().strftime("%Y-%m-%d %H:%M"))
        if success:
            applied_count += 1

    # 8. Send digest email
    send_digest(len(qualified), applied_count, auto_apply[:5])
    print(f"\n=== Done. {len(qualified)} logged · {applied_count} applied ===")

async def attempt_apply(job: dict, cover_letter: str) -> bool:
    """
    Placeholder for Playwright-based form filler.
    Returns True if successfully applied, False if needs manual intervention.
    Platform-specific apply logic goes here (LinkedIn Easy Apply, etc.)
    """
    from playwright.async_api import async_playwright
    # NOTE: LinkedIn Easy Apply, Indeed Quick Apply, etc. each need
    # their own sub-handler. Scaffold is here — full implementation 
    # in next step once you confirm repo is set up.
    print(f"    Applying to: {job['title']} @ {job['company']} (score: {job['match_score']})")
    return False  # set to True once apply handlers are implemented

def send_digest(total: int, applied: int, top_jobs: list[dict]):
    gmail_user = os.environ.get("YOUR_GMAIL", "")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD", "")
    if not gmail_user or not gmail_pass:
        return
    body = f"""Daily Job Automation Digest — {datetime.now().strftime('%Y-%m-%d')}

Jobs logged to Sheets: {total}
Auto-applied: {applied}

Top matches today:
"""
    for j in top_jobs:
        body += f"\n• [{j['match_score']}/100] {j['title']} @ {j['company']} — {j.get('salary','N/A')}\n  {j['url']}\n"

    body += "\nView full tracker: https://docs.google.com/spreadsheets"
    msg = MIMEText(body)
    msg["Subject"] = f"Job Bot Digest — {total} jobs, {applied} applied"
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(gmail_user, gmail_pass)
            s.sendmail(gmail_user, gmail_user, msg.as_string())
        print("[7] Digest email sent.")
    except Exception as e:
        print(f"[7] Email failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_pipeline())