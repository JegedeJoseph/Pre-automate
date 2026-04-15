# Implementation Checklist & Quick Start

## ✅ Phase 1: Core Implementation (COMPLETED)

- [x] **scraper.py** - Enhanced with retry logic, logging, better selectors
  - [x] RemoteOK scraper (improved)
  - [x] WeWorkRemotely scraper (improved)
  - [x] Simplify.jobs scraper (complete)
  - [x] LinkedIn/Indeed/Glassdoor/Wellfound scaffolds (placeholders)

- [x] **applier.py** - NEW module for auto-apply handlers
  - [x] RemoteOK apply handler (click buttons)
  - [x] WeWorkRemotely apply handler (click buttons)
  - [x] Simplify apply handler (with Greenhouse form filler)
  - [x] LinkedIn/Indeed placeholders

- [x] **main.py** - Updated pipeline with real apply logic
  - [x] Proper logging and error handling
  - [x] Email digest on successful applications
  - [x] Status updates to Google Sheets

- [x] **scorer.py** - No changes needed (already solid)

- [x] **cover_letter.py** - No changes needed (already solid)

- [x] **sheets_logger.py** - No changes needed (already solid)

- [x] **requirements.txt** - Updated with all dependencies

- [x] **README.md** - Comprehensive setup guide

- [x] **.env.example** - Environment template

---

## 🔧 Phase 2: Setup (YOU DO THIS)

### Step 1: Environment Setup
```bash
# Python 3.11+
python --version

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Google Cloud Setup

1. Go to: https://console.cloud.google.com/
2. Create new project
3. Enable APIs:
   - Google Sheets API
   - Google Drive API
4. Create Service Account:
   - IAM & Admin > Service Accounts > Create Service Account
   - Generate JSON key
5. Create Google Sheet:
   - Go to https://sheets.google.com
   - Create new sheet named "Zain Job Tracker"
   - Share with service account email (e.g., `zain-bot@project.iam.gserviceaccount.com`)

### Step 3: Anthropic API Setup

1. Go to: https://console.anthropic.com/
2. Create API key
3. Copy to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

### Step 4: Gmail Setup

1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Create App Password (under "App passwords")
4. Copy to `.env`: `GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx`

### Step 5: Create .env File

```bash
# Copy from template
cp .env.example .env

# Edit .env with your values
# GOOGLE_CREDENTIALS_JSON='...' (full JSON from Service Account key)
# YOUR_GMAIL=your.email@gmail.com
# GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
# ANTHROPIC_API_KEY=sk-ant-...
# APPLICANT_NAME=Your Full Name
# APPLICANT_EMAIL=your.email@gmail.com
# SHEET_ID=... (from Google Sheet URL)
```

### Step 6: Test Locally

```bash
# Load environment
export $(cat .env | xargs)  # Unix/Mac
# Windows: manually set env vars or use .env loader

# Run pipeline
python main.py

# Watch output for:
# ✓ [1] Loaded sheet
# ✓ [2] Scraped X jobs
# ✓ [3] X new jobs
# ✓ [4] X qualified, Y for auto-apply
# ✓ [5] Generated cover letters
# ✓ [6] Logged to Google Sheets
# ✓ [7] Applied to jobs
```

---

## 🚀 Phase 3: GitHub Actions Deployment

### Step 1: Push to GitHub

```bash
git add -A
git commit -m "Add job automation bot with auto-apply handlers"
git push origin main
```

### Step 2: Add Secrets to GitHub

1. Go to GitHub repo > Settings > Secrets and variables > Actions
2. Add new secret for each variable:

| Secret Name | Value |
|---|---|
| GOOGLE_CREDENTIALS_JSON | `{"type":"service_account",...}` (full JSON) |
| YOUR_GMAIL | your.email@gmail.com |
| GMAIL_APP_PASSWORD | xxxx xxxx xxxx xxxx |
| ANTHROPIC_API_KEY | sk-ant-... |
| APPLICANT_NAME | Your Full Name |
| APPLICANT_EMAIL | your.email@gmail.com |
| SHEET_ID | abc...xyz (from Sheet URL) |

### Step 3: Test GitHub Actions

1. Go to Actions tab
2. Select "Daily Job Automation"
3. Click "Run workflow" > "Run workflow"
4. Check output in logs

---

## 📊 Phase 4: Monitoring & Optimization

### Monitor First Week

- [ ] Check Google Sheets for new jobs appearing
- [ ] Review match scores and keywords
- [ ] Verify auto-apply successes/failures
- [ ] Check email digest for correct formatting
- [ ] Look for any scraper errors in logs

### Optimize Based on Results

**If too many low-quality jobs:**
- Increase threshold from 60 to 70
- Add negative keywords to filter out
- Refine salary expectations

**If missing high-quality jobs:**
- Decrease threshold from 60 to 50
- Add relevant keywords to ZAIN_KEYWORDS
- Check if scrapers are working

**If auto-apply failing on specific platforms:**
- Update selectors in `applier.py`
- Add special handling for that platform
- May need manual application for complex forms

---

## 🎯 Phase 5: LinkedIn & Indeed (When Credentials Ready)

### For LinkedIn Easy Apply:

1. Get LinkedIn session cookies
2. Implement in `scraper.py`:
   ```python
   async def scrape_linkedin() -> list[dict]:
       # Use cookies to login
       # Search for your target jobs
       # Extract job listings
   ```
3. Implement in `applier.py`:
   ```python
   async def apply_linkedin_easyapply(self, job, cover_letter):
       # Fill LinkedIn Easy Apply form
       # Submit application
   ```

### For Indeed Quick Apply:

1. Get Indeed session cookies
2. Implement scraper and applier (similar to LinkedIn)

---

## 📝 Troubleshooting Checklist

### Scrapers returning 0 jobs
- [ ] Playwright chromium installed: `playwright install chromium`
- [ ] Internet connection working
- [ ] Run individual scraper test
- [ ] Check website selectors haven't changed

### Google Sheets not updating
- [ ] GOOGLE_CREDENTIALS_JSON valid JSON format
- [ ] Service account email shared on Sheet
- [ ] "Zain Job Tracker" Sheet exists
- [ ] All rows inserted to correct sheet

### Cover letters not generating
- [ ] ANTHROPIC_API_KEY valid
- [ ] Check API usage at console.anthropic.com
- [ ] Verify Claude model name in code matches API

### Auto-apply not working
- [ ] Check logs for specific errors
- [ ] Update selectors if website changed
- [ ] Test manually on platform first
- [ ] May need custom handlers for different ATS

### Email digest not sending
- [ ] GMAIL_APP_PASSWORD is correct (not regular password)
- [ ] 2FA enabled on Gmail account
- [ ] YOUR_GMAIL correct
- [ ] Digest only sends on successful applies (≥1)

---

## 🔍 Debugging Commands

```python
# Test individual scraper
import asyncio
from scraper import scrape_remoteok
jobs = asyncio.run(scrape_remoteok())
print(f"Jobs found: {len(jobs)}")

# Test scoring
from scorer import filter_and_score
qualified = filter_and_score(jobs, threshold=60)
print(f"Qualified: {len(qualified)}")

# Test cover letter generation
import os
os.environ['ANTHROPIC_API_KEY'] = 'your-key'
from cover_letter import generate_cover_letter
letter = asyncio.run(generate_cover_letter(jobs[0]))
print(letter)

# Test Google Sheets connection
from sheets_logger import get_sheet
ws = get_sheet()
print(f"Sheet loaded: {ws.title}")
```

---

## ✨ Success Metrics

After 2 weeks running, you should see:

- [ ] 50-100+ jobs scraped per run
- [ ] 10-20+ jobs qualifying (≥60 score)
- [ ] 5-10 jobs for auto-apply (≥70 score)
- [ ] 3-7 successful auto-applies per run
- [ ] 2-5 recruiter responses per week
- [ ] 1-3 phone interviews per week
- [ ] Resume tailored for each application

---

## 📞 Support & Next Steps

1. **Setup**: Follow Phase 2 step-by-step
2. **Test**: Run `python main.py` locally
3. **Deploy**: Push to GitHub and add secrets
4. **Monitor**: Check first week of runs
5. **Optimize**: Adjust thresholds/keywords based on results

**Questions?** Check README.md Troubleshooting section.

Good luck! 🚀
