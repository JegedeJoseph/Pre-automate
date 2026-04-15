# 🤖 Zain Job Automation Bot

**Automate job scraping, scoring, and application for maximum efficiency.**

This bot scrapes jobs from free/public platforms, scores them against your profile, generates personalized cover letters, and applies automatically.

---

## 🎯 Features

✅ **Multi-Platform Scraping**
- RemoteOK, WeWorkRemotely, Simplify.jobs (free/public)
- Scaffolds for LinkedIn, Indeed, Glassdoor, Wellfound (future)

✅ **Intelligent Job Scoring**
- Keyword matching (40 matched skills / 100)
- Title relevance
- Salary validation ($140K+ floor)
- Remote/USA/Canada location filter
- Seniority signals

✅ **Automated Cover Letters**
- Claude API generated personalized letters
- Context-aware from job description
- Tailored to role and company

✅ **Auto-Apply**
- RemoteOK & WeWorkRemotely: Click apply buttons
- Greenhouse form filling (auto-populate email, name, cover letter)
- Manual fallback for complex applications

✅ **Tracking & Notifications**
- Google Sheets integration (tracking all jobs)
- Daily digest email (only on successful applies)
- Job deduplication across runs

---

## 🚀 Setup

### 1. Prerequisites

```bash
# Python 3.11+
# Git

# Clone repo
git clone <your-repo>
cd Pre-automate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### 2. Environment Configuration

**Create `.env` file** (copy from `.env.example`):

```env
# Google Sheets Service Account JSON (from Google Cloud Console)
GOOGLE_CREDENTIALS_JSON='{"type":"service_account","project_id":"...","...":""}'

# Your Gmail for digest emails
YOUR_GMAIL=your.email@gmail.com

# Gmail app password (enable 2FA at myaccount.google.com, generate app password)
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Anthropic API key (from console.anthropic.com)
ANTHROPIC_API_KEY=sk-ant-v0-...

# Your info (for form filling)
APPLICANT_NAME="Your Full Name"
APPLICANT_EMAIL=your.email@gmail.com

# Google Sheets ID (from your sheet URL)
SHEET_ID=1abc...xyz
```

### 3. Google Sheets Integration

1. **Create Google Cloud Project**: https://console.cloud.google.com/
2. **Enable APIs**: Google Sheets API, Google Drive API
3. **Create Service Account**: Create credentials > Service Account
4. **Download JSON key** and set `GOOGLE_CREDENTIALS_JSON`
5. **Share your Google Sheet** with the service account email

### 4. Test Locally

```bash
# Set environment variables
export $(cat .env | xargs)

# Run pipeline
python main.py

# Expected output:
# === Zain Job Automation Pipeline ===
# [1] Loaded sheet. X jobs already tracked.
# [2] Scraped Y raw jobs.
# [3] X new jobs after dedup.
# [4] X qualified (score ≥ 60) · Y for auto-apply (score ≥ 70)
# [5] Generated cover letters...
# [6] Logging to Google Sheets...
# [7] Auto-applying...
# === Done. X logged · Y applied ===
```

---

## 🔄 GitHub Actions Schedule

**File**: `.github/workflows/run_daily.yml`

Runs **7 AM EST, Monday–Friday** (configurable with cron)

**Setup**:
1. Go to GitHub repo > Settings > Secrets and variables > Actions
2. Add all `.env` variables as secrets:
   - `GOOGLE_CREDENTIALS_JSON`
   - `YOUR_GMAIL`
   - `GMAIL_APP_PASSWORD`
   - `ANTHROPIC_API_KEY`
   - `APPLICANT_NAME`
   - `APPLICANT_EMAIL`
   - `SHEET_ID`

3. Trigger manually: Actions tab > "Daily Job Automation" > "Run workflow"

---

## 📊 Project Structure

```
Pre-automate/
├── main.py                 # Pipeline orchestration
├── scraper.py             # Job scrapers (RemoteOK, WeWorkRemotely, Simplify)
├── scorer.py              # Job matching & scoring logic
├── cover_letter.py        # Claude API cover letter generator
├── applier.py             # Auto-apply handlers per platform
├── sheets_logger.py       # Google Sheets integration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .github/
│   └── workflows/
│       └── run_daily.yml  # GitHub Actions scheduler
└── README.md
```

---

## 🔧 Scoring System

**Total: 100 points**

| Factor | Points | Criteria |
|--------|--------|----------|
| Keywords | 35 | Matched skills from your profile |
| Title | 20 | Job title matches target roles |
| Salary | 20 | ≥$140K (partial if unknown) |
| Location | 15 | Remote in USA/Canada |
| Seniority | 10 | Senior/Lead/Staff/Principal title |

**Qualification threshold**: ≥60 points
**Auto-apply threshold**: ≥70 points

---

## 🎯 Your Profile

**Current**: Zain Malik, Senior SWE @ Google

- **Experience**: 10+ years (Executive level)
- **Stack**: Python, Java, TypeScript, GCP, AWS, LLMs, Kubernetes, Kafka, etc.
- **Achievements**: 7-engineer team lead, 40% workflow automation, 99.99% uptime
- **Keywords**: Multi-agent orchestration, Vertex AI, distributed systems, React, Angular

*Edit in `cover_letter.py` and `scorer.py` to personalize for your profile.*

---

## 🚨 Troubleshooting

### "No jobs scraped"
- Check internet connection
- Verify Playwright chromium installed: `playwright install chromium`
- Try running individual scrapers in Python shell:
  ```python
  import asyncio
  from scraper import scrape_remoteok
  jobs = asyncio.run(scrape_remoteok())
  print(len(jobs))
  ```

### "Google Sheets not found"
- Verify `GOOGLE_CREDENTIALS_JSON` is valid JSON
- Check service account email is shared on your Sheet
- Ensure "Zain Job Tracker" sheet exists or will be auto-created

### "Cover letters not generating"
- Verify `ANTHROPIC_API_KEY` is valid
- Check API quota at console.anthropic.com
- Review logs for API errors

### "Auto-apply failing"
- Some jobs require manual application (common)
- Check logs for which selector failed
- Update `applier.py` with new selectors if needed
- Companies using different ATS (Greenhouse, Lever, etc.) may need custom handlers

### "GitHub Actions failing"
- Check Actions tab > workflow logs
- Verify all secrets are set correctly
- Look for platform-specific errors in logs

---

## 📝 Customization

### Add New Platform Scraper

1. **Create function in `scraper.py`**:
```python
async def scrape_myplatform() -> list[dict]:
    """Scrape MyPlatform for jobs."""
    jobs = []
    # ... scraping logic ...
    return jobs
```

2. **Add to `run_all_scrapers()`**:
```python
tasks = [
    scrape_remoteok(),
    scrape_weworkremotely(),
    scrape_simplify(),
    scrape_myplatform(),  # NEW
]
```

3. **Add apply handler in `applier.py`**:
```python
async def apply_myplatform(self, job: dict, cover_letter: str) -> bool:
    # ... form filling logic ...
```

### Adjust Scoring Weights

Edit `scorer.py`:
```python
ZAIN_KEYWORDS = [...]  # Add/remove keywords
TARGET_TITLES = [...]  # Edit target roles
SALARY_FLOOR = 140_000  # Adjust minimum salary
```

### Change Application Thresholds

Edit `main.py`:
```python
qualified = filter_and_score(new_jobs, threshold=60)  # Qualification threshold
auto_apply = [j for j in qualified if j["match_score"] >= 70]  # Auto-apply threshold
```

---

## 📋 Next Steps

- [ ] Get LinkedIn credentials ready (for LinkedIn Easy Apply)
- [ ] Set up Indeed cookies/integration (for Indeed Quick Apply)
- [ ] Test full pipeline end-to-end
- [ ] Monitor first week of automated applications
- [ ] Refine selectors based on actual platform changes
- [ ] Add Glassdoor & Wellfound scrapers

---

## 🤝 Contributing

Found issues? Have improvements?

1. Update relevant module
2. Test locally: `python main.py`
3. Push to GitHub
4. GitHub Actions will run on next schedule

---

## 📞 Support

- Check logs in `.github/workflows/run_daily.yml` > Actions tab
- Review `TROUBLESHOOTING` section above
- Enable debug logging in scripts with `logging.basicConfig(level=logging.DEBUG)`

---

**Built with ❤️ for maximum job automation efficiency.**
