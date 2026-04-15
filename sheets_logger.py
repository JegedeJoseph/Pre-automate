# sheets_logger.py
import gspread
from google.oauth2.service_account import Credentials
import json, os

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = "Zain Job Tracker"
HEADERS = [
    "Job ID", "Date Scraped", "Platform", "Title", "Company",
    "Location", "Salary", "Match Score", "Keywords Matched",
    "Job URL", "Apply URL", "Cover Letter", "Status", "Applied Date",
    "Response", "Notes"
]

def get_sheet():
    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    gc = gspread.authorize(creds)
    try:
        sh = gc.open(SHEET_NAME)
    except gspread.exceptions.SpreadsheetNotFound:
        sh = gc.create(SHEET_NAME)
        sh.share(os.environ["YOUR_GMAIL"], perm_type="user", role="writer")
    ws = sh.sheet1
    if ws.row_count == 0 or ws.cell(1, 1).value != "Job ID":
        ws.insert_row(HEADERS, 1)
    return ws

def get_seen_ids(ws) -> set:
    try:
        col = ws.col_values(1)
        return set(col[1:])  # skip header
    except Exception:
        return set()

def append_jobs(ws, jobs: list[dict], cover_letters: dict):
    rows = []
    for job in jobs:
        rows.append([
            job.get("job_id", ""),
            job.get("date_scraped", ""),
            job.get("platform", ""),
            job.get("title", ""),
            job.get("company", ""),
            job.get("location", ""),
            job.get("salary", ""),
            job.get("match_score", ""),
            job.get("keywords_matched", ""),
            job.get("url", ""),
            job.get("apply_url", ""),
            cover_letters.get(job.get("job_id", ""), ""),
            "Pending",
            "",
            "",
            ""
        ])
    if rows:
        ws.append_rows(rows, value_input_option="USER_ENTERED")

def update_status(ws, job_id: str, status: str, applied_date: str = ""):
    col_a = ws.col_values(1)
    try:
        row_idx = col_a.index(job_id) + 1
        ws.update_cell(row_idx, 13, status)       # Status column
        ws.update_cell(row_idx, 14, applied_date) # Applied Date column
    except ValueError:
        pass