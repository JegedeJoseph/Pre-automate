# Quick Reference & Commands

## 🚀 Quick Start

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt
playwright install chromium

# 2. Configure
cp .env.example .env
# Edit .env with your values

# 3. Test
python main.py

# 4. Deploy
git add -A
git commit -m "Deploy job automation bot"
git push origin main
# Then add secrets to GitHub
```

---

## 🔍 Debugging Commands

```python
# Python shell for quick testing

# 1. Test scraping
import asyncio
from scraper import scrape_remoteok, scrape_weworkremotely, scrape_simplify

jobs = asyncio.run(scrape_remoteok())
print(f"RemoteOK: {len(jobs)} jobs")

jobs = asyncio.run(scrape_weworkremotely())
print(f"WeWorkRemotely: {len(jobs)} jobs")

jobs = asyncio.run(scrape_simplify())
print(f"Simplify: {len(jobs)} jobs")

# 2. Test scoring
from scorer import score_job, filter_and_score
all_jobs = []
all_jobs.extend(asyncio.run(scrape_remoteok()))
all_jobs.extend(asyncio.run(scrape_weworkremotely()))
all_jobs.extend(asyncio.run(scrape_simplify()))

qualified = filter_and_score(all_jobs, threshold=60)
print(f"Qualified: {len(qualified)} jobs")

for job in qualified[:5]:
    print(f"  {job['match_score']:3}/100 | {job['title'][:30]:30} @ {job['company'][:20]:20} | {job.get('salary', 'N/A')}")

# 3. Test Google Sheets connection
from sheets_logger import get_sheet, get_seen_ids
ws = get_sheet()
print(f"Sheet: {ws.title}")
seen = get_seen_ids(ws)
print(f"Tracked jobs: {len(seen)}")

# 4. Test cover letter generation
import os
os.environ['ANTHROPIC_API_KEY'] = 'your-key'
from cover_letter import generate_cover_letter

job = qualified[0]
letter = asyncio.run(generate_cover_letter(job))
print(f"Letter:\n{letter}")

# 5. Test apply handler
from applier import JobApplier
applier = JobApplier()
success = asyncio.run(applier.apply_remoteok(job, "Sample letter"))
print(f"Apply result: {success}")

# 6. Full pipeline test
exec(open('main.py').read())
```

---

## 📊 Key Files & Locations

| File | Purpose | Modify For |
|------|---------|-----------|
| main.py | Pipeline orchestration | Thresholds, timing, email logic |
| scraper.py | Job scrapers | Add platforms, fix selectors |
| applier.py | Auto-apply handlers | Add form fields, new ATS systems |
| scorer.py | Job matching | Keywords, title relevance, salary |
| cover_letter.py | Letter generation | Zain's resume/profile |
| sheets_logger.py | Google Sheets tracking | Column names, sheet ID |
| .github/workflows/run_daily.yml | GitHub Actions schedule | Cron expression, Python version |

---

## 🔧 Configuration Variables

```env
# Required
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
YOUR_GMAIL=email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
ANTHROPIC_API_KEY=sk-ant-...
APPLICANT_NAME=Your Name
APPLICANT_EMAIL=email@gmail.com
SHEET_ID=abc...xyz

# Optional
LINKEDIN_SESSION_ID=  (future)
INDEED_SESSION_ID=   (future)
```

---

## 🎯 Job Scoring Breakdown

```
100 points total:
  35 - Keywords (matched from your profile)
  20 - Title (matches target roles)
  20 - Salary (≥$140K)
  15 - Location (Remote, USA/Canada)
  10 - Seniority (Senior/Lead/Staff/Principal)

Thresholds:
  ≥60 = Qualified (logged to Sheets)
  ≥70 = Auto-apply (attempted)
```

---

## 📋 Target Roles & Keywords

### Roles
```
Senior Software Engineer
Software Engineer
AI Engineer
Machine Learning Engineer
Backend Engineer
Full Stack Engineer
```

### Tech Stack Keywords
```
Python, Java, TypeScript, JavaScript
GCP, AWS, Azure
LLM, Vertex AI, Google ADK
Multi-agent, Generative AI
Kafka, Kubernetes, BigQuery
React, Angular, Node.js
Docker, CI/CD, Microservices
```

---

## 🚨 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `No jobs scraped` | Website changed selectors | Update selectors in scraper.py |
| `ModuleNotFoundError: applier` | applier.py not in directory | Check file exists in repo root |
| `Google Sheets not found` | Credentials invalid | Verify GOOGLE_CREDENTIALS_JSON in .env |
| `Claude API error` | Invalid API key | Check ANTHROPIC_API_KEY format |
| `Email not sent` | Wrong Gmail password | Use app password, not main password |
| `Auto-apply failed` | Website structure changed | Update selectors in applier.py |
| `GitHub Actions failing` | Missing secrets | Add all secrets to GitHub repo settings |

---

## 🔑 GitHub Secrets Setup

```bash
# In GitHub repo > Settings > Secrets and variables > Actions
# Add these secrets:

GOOGLE_CREDENTIALS_JSON
YOUR_GMAIL
GMAIL_APP_PASSWORD
ANTHROPIC_API_KEY
APPLICANT_NAME
APPLICANT_EMAIL
SHEET_ID
```

---

## 📈 Performance Tips

```python
# Reduce API calls (Anthropic charges per token)
# Only generate letters for top 5 jobs:
auto_apply = filter_and_score(new_jobs, threshold=70)[:5]

# Speed up scraping (parallel platforms)
# Already implemented in scraper.py with asyncio

# Reduce email overhead
# Only send if applied_count > 0 (already implemented)

# Cache job descriptions
# Already scraped and stored with each job
```

---

## 🐛 Enable Debug Logging

```python
# In main.py, set logging level to DEBUG
import logging
logging.basicConfig(level=logging.DEBUG)

# Now you'll see all detailed logs including:
# - Scraper attempts and retries
# - Apply handler details
# - API call times
# - Selector matching details
```

---

## 📞 Support Checklist

Before asking for help:
- [ ] Check README.md Troubleshooting section
- [ ] Check IMPLEMENTATION.md setup steps
- [ ] Review error logs in GitHub Actions
- [ ] Test individual module in Python shell
- [ ] Check .env file has all required variables
- [ ] Verify GitHub secrets are set correctly

---

## 🔄 Monitoring Commands

```bash
# Check GitHub Actions logs
# URL: github.com/YOUR_ORG/Pre-automate/actions

# Monitor locally
tail -f main.py  # Check for new output

# Check Google Sheets programmatically
python -c "
from sheets_logger import get_sheet
ws = get_sheet()
jobs_today = len(ws.col_values(2)[1:])  # Date scraped column
print(f'Jobs logged today: {jobs_today}')
"
```

---

**Last Updated**: April 15, 2026
**Status**: ✅ Ready to Deploy
