# Job Scraper Application - Setup & Usage Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy and customize `.env.example` to `.env`:
```bash
cp .env.example .env
```

Update `.env` with your preferences:
```env
RESUME_FILE_PATH=./data/sample_resume.txt
HEADLESS_BROWSER=true
DEFAULT_PAGES_TO_SCRAPE=3
```

### 3. Run Test (Optional)
Verify everything works:
```bash
python test_app.py
```

### 4. Run Full Pipeline
```bash
python main.py
```

---

## 📋 Configuration Guide

### Resume Setup
Place your resume in the `data/` folder or update `RESUME_FILE_PATH` in `.env`:
- **Supported formats**: PDF, DOCX, TXT
- **Example**: `RESUME_FILE_PATH=./data/my_resume.pdf`

### Job Preferences (preferences.json)
```json
{
  "target_titles": ["Python Developer", "Backend Engineer"],
  "required_skills": ["Python"],
  "nice_to_have_skills": ["Django", "FastAPI"],
  "min_salary": 80000,
  "max_salary": 200000,
  "locations": ["Remote", "San Francisco"],
  "remote_preference": "any",
  "job_types": ["Full-time"],
  "min_match_score": 50.0
}
```

### Google Sheets Export (Optional)
Set up Google Sheets integration for automatic result export:

1. Create Google service account credentials
2. Add to `.env`:
```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
SPREADSHEET_ID=your_sheet_id
```

---

## 🔍 Core Components

### Resume Parser (`src/resume/parser.py`)
- Extracts name, email, phone, location, skills
- Detects 40+ technology skills
- Supports PDF, DOCX, TXT formats

### Job Scrapers (`src/scraper/`)
- **Indeed**: Large job database, consistent formatting
- **LinkedIn**: Professional network, high-quality listings
- **Glassdoor**: Company reviews + salary data
- Runs asynchronously for speed

### Skill Matcher (`src/scraper/matcher.py`)
- Calculates match scores (0-100%)
- Fuzzy matching for similar skills
- Filters by salary, location, company
- Handles remote/hybrid preferences

### Data Models (`src/models/`)
- `JobListing`: Structured job data
- `Resume`: Parsed resume information
- `JobPreferences`: Search criteria

---

## 📊 Data Export

### Local JSON Export
Results automatically saved to `data/results.json`:
```json
{
  "title": "Senior Python Developer",
  "company": "Tech Corp",
  "location": "Remote",
  "match_score": 85.5,
  "matched_skills": ["Python", "Django"],
  "missing_skills": ["Kubernetes"]
}
```

### Google Sheets Export
Automatically appends rows with:
- Job title, company, location, link
- Match score and skill analysis
- Salary, job type, source

---

## 🛠 Advanced Usage

### Custom Search Parameters
```python
await app.run_full_pipeline(
    search_query="Backend Engineer",
    location="San Francisco",
    pages=5,
    sources=["indeed", "linkedin", "glassdoor"]
)
```

### Programmatic Access
```python
from src.scraper.jobs import JobScraper
from src.scraper.matcher import SkillMatcher

scraper = JobScraper()
jobs = await scraper.scrape_all("Python Developer", pages=3)
matched = matcher.filter_jobs(jobs)
```

---

## 📝 Logging

Logs are written to `./logs/app.log` with configurable levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General application flow
- `WARNING`: Potential issues
- `ERROR`: Application errors

View in real-time:
```bash
tail -f logs/app.log  # macOS/Linux
Get-Content logs/app.log -Wait  # Windows PowerShell
```

---

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Resume file not found" | Check `RESUME_FILE_PATH` in `.env` |
| No jobs found | Try different keywords, increase pages |
| Scraper timeout | Increase `BROWSER_TIMEOUT` in `.env` |
| Google Sheets error | Verify credentials and sheet permissions |
| Python import errors | Run `pip install -r requirements.txt` |

---

## 🎯 Workflow

1. **Prepare Resume** → Place in `data/` folder
2. **Set Preferences** → Edit `preferences.json`
3. **Run Test** → `python test_app.py`
4. **Execute Pipeline** → `python main.py`
5. **Review Results** → Check `data/results.json` or Google Sheets
6. **Refine Preferences** → Adjust and run again

---

## 📚 Project Files

| File | Purpose |
|------|---------|
| `main.py` | Application entry point |
| `test_app.py` | Demo and testing script |
| `requirements.txt` | Python dependencies |
| `preferences.json` | Job search criteria |
| `.env` | Environment configuration |
| `README.md` | Full documentation |

---

## 💡 Tips & Best Practices

✅ **Do:**
- Start with 1-2 page scrapes to test
- Use specific job titles and locations
- Review match scores before applying
- Save results for comparison
- Update preferences based on results

❌ **Don't:**
- Scrape without proper delays (respect job boards)
- Use generic keywords
- Ignore missing critical skills
- Mix remote and onsite preferences (use "any")

---

## 🔄 Typical Workflow

```
Start → Load Resume → Parse Skills → Load Preferences
  ↓
Scrape Indeed → Scrape LinkedIn → Scrape Glassdoor
  ↓
Match Skills → Filter by Preferences → Score & Rank
  ↓
Export to JSON ← Export to Google Sheets
  ↓
Review Results → Apply to Jobs
```

---

## 📞 Support

For issues:
1. Check logs: `cat logs/app.log`
2. Run test: `python test_app.py`
3. Verify configuration in `.env`
4. Review README.md for more details

---

**Happy job hunting! 🎉**
