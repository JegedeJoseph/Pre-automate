# Job Scraper & Matcher

A comprehensive Python application that scrapes job listings from multiple job boards (Indeed, LinkedIn, Glassdoor), matches them against your resume and job preferences, and exports results to Google Sheets or local JSON files.

## Features

✨ **Multi-Source Scraping**
- Scrape jobs from Indeed, LinkedIn, and Glassdoor
- Asynchronous scraping for faster performance
- Duplicate detection and removal

🧠 **Smart Resume Parsing**
- Extract information from PDF, DOCX, and TXT resumes
- Automatic skill detection from resume text
- Support for multiple skill categories

🎯 **Intelligent Job Matching**
- Match job requirements against resume skills
- Fuzzy matching for similar skills
- Configurable match score thresholds

📊 **Preference-Based Filtering**
- Filter by job title, location, salary range
- Remote/hybrid/on-site preferences
- Excluded keywords and companies
- Minimum match score requirements

📈 **Export Options**
- Export results to Google Sheets (with real-time sync)
- Save results as local JSON files
- Detailed match scoring and analysis

## Project Structure

```
Pre-automate/
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
├── preferences.json          # Job search preferences
├── .env                       # Environment configuration
├── src/
│   ├── config.py             # Configuration and data models
│   ├── resume/
│   │   ├── __init__.py
│   │   └── parser.py         # Resume parsing logic
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── jobs.py           # Job scraper orchestrator
│   │   ├── indeed.py         # Indeed scraper
│   │   ├── linkedin.py       # LinkedIn scraper
│   │   ├── glassdoor.py      # Glassdoor scraper
│   │   └── matcher.py        # Skill matching logic
│   ├── sheets/
│   │   ├── __init__.py
│   │   └── integration.py    # Google Sheets integration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── resume.py         # Resume data model
│   │   ├── job.py            # Job listing data model
│   │   └── preferences.py    # Job preferences model
│   └── utils/
│       ├── __init__.py
│       ├── config.py         # Application configuration
│       └── logger.py         # Logging setup
├── data/
│   ├── sample_resume.txt    # Sample resume for testing
│   └── results.json         # Saved results
└── logs/
    └── app.log              # Application logs
```

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Pre-automate
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and update with your configuration:
```bash
cp .env.example .env
```

Edit `.env`:
```env
# Google Sheets (Optional)
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
SPREADSHEET_ID=your_sheet_id

# Scraper Settings
HEADLESS_BROWSER=true
BROWSER_TIMEOUT=30000
DEFAULT_PAGES_TO_SCRAPE=3

# Resume File Path
RESUME_FILE_PATH=./data/sample_resume.txt

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

## Quick Start

### 1. Create a Preferences File

Create `preferences.json` in the project root:
```json
{
  "target_titles": ["Python Developer", "Backend Engineer"],
  "required_skills": ["Python"],
  "nice_to_have_skills": ["Django", "FastAPI", "PostgreSQL"],
  "min_salary": 80000,
  "max_salary": 200000,
  "locations": ["Remote", "San Francisco"],
  "remote_preference": "any",
  "job_types": ["Full-time"],
  "min_match_score": 50.0
}
```

### 2. Prepare Your Resume

Place your resume in the `data/` directory. Supported formats:
- `.pdf` - PDF files
- `.docx` - Microsoft Word documents
- `.txt` - Plain text files

Or update `RESUME_FILE_PATH` in `.env` to point to your resume.

### 3. Run the Application

```bash
python main.py
```

## Configuration

### Resume File
Update the `RESUME_FILE_PATH` in `.env` to point to your resume file:
```env
RESUME_FILE_PATH=./data/my_resume.pdf
```

### Job Preferences
Edit `preferences.json` to customize your job search:
```json
{
  "target_titles": ["Software Engineer", "Backend Developer"],
  "required_skills": ["Python", "JavaScript"],
  "nice_to_have_skills": ["Docker", "Kubernetes", "AWS"],
  "min_salary": 100000,
  "max_salary": 250000,
  "locations": ["Remote", "New York"],
  "remote_preference": "remote_only",  // "any", "remote_only", "hybrid", "onsite"
  "job_types": ["Full-time"],
  "excluded_companies": ["BadCorp"],
  "excluded_keywords": ["legacy", "old"],
  "min_match_score": 60.0
}
```

### Google Sheets Export (Optional)

To export results to Google Sheets:

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable Google Sheets API

2. **Create Service Account**
   - Go to Service Accounts
   - Create a new service account
   - Create a JSON key file
   - Download the key

3. **Configure Credentials**
   - Place the JSON file in a secure location
   - Update `.env`:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
   SPREADSHEET_ID=your_sheet_id_from_url
   ```

4. **Share the Sheet**
   - Share your Google Sheet with the service account email
   - Use the email from the JSON file (client_email field)

## Usage Examples

### Basic Usage
```python
import asyncio
from main import JobScraperApplication

async def main():
    app = JobScraperApplication(
        resume_path="./data/my_resume.pdf",
        preferences_path="preferences.json"
    )
    
    await app.run_full_pipeline(
        search_query="Python Developer",
        location="Remote",
        pages=3,
        sources=["indeed"],
        save_local=True
    )

asyncio.run(main())
```

### Advanced Usage
```python
# Scrape from multiple sources
await app.run_full_pipeline(
    search_query="Backend Engineer",
    location="San Francisco",
    pages=5,
    sources=["indeed", "linkedin", "glassdoor"],
    export_sheets=True,
    save_local=True
)
```

## Data Models

### Resume
```python
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-123-4567",
  "location": "San Francisco, CA",
  "skills": ["Python", "Django", "PostgreSQL"],
  "experience": [...],
  "education": [...],
  "certifications": [...]
}
```

### JobListing
```python
{
  "title": "Senior Python Developer",
  "company": "Tech Corp",
  "location": "San Francisco, CA",
  "link": "https://example.com/job/123",
  "description": "We are looking for...",
  "salary": "$120,000 - $160,000",
  "job_type": "Full-time",
  "source": "Indeed",
  "match_score": 85.5,
  "matched_skills": ["Python", "Django"],
  "missing_skills": ["Kubernetes"]
}
```

## Logging

Application logs are written to `./logs/app.log`. Configure logging level in `.env`:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=./logs/app.log
```

## Troubleshooting

### Resume Parsing Issues
- Ensure resume file format is supported (PDF, DOCX, TXT)
- For PDF files, make sure PyPDF2 is installed: `pip install PyPDF2`
- For DOCX files, ensure python-docx is installed: `pip install python-docx`

### Scraper Issues
- Check internet connection
- Verify Playwright is installed: `pip install playwright`
- Run `playwright install chromium` to download browser

### Google Sheets Issues
- Verify credentials JSON file is valid
- Ensure service account email has access to the sheet
- Check that SPREADSHEET_ID is correct from the sheet URL

### No Jobs Found
- Try different search queries
- Increase the number of pages to scrape
- Check job board websites directly to verify jobs exist
- Verify your preferences aren't too restrictive

## Dependencies

- **playwright**: Headless browser automation
- **pydantic**: Data validation and modeling
- **python-dotenv**: Environment variable management
- **google-auth-oauthlib**: Google authentication
- **google-api-python-client**: Google Sheets API client
- **PyPDF2**: PDF file processing
- **requests**: HTTP client library
- **beautifulsoup4**: HTML parsing
- **lxml**: XML/HTML processing

## Performance Tips

- Use `HEADLESS_BROWSER=true` in `.env` for faster scraping
- Limit pages to scrape to reduce execution time
- Increase `BROWSER_TIMEOUT` if you have slow internet
- Use `min_match_score` to filter results quickly

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions:
1. Check the Troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with details

## Roadmap

- [ ] Add Dice.com scraper
- [ ] Add ZipRecruiter scraper
- [ ] Implement email notifications for new jobs
- [ ] Add job application tracking
- [ ] Implement machine learning for better job matching
- [ ] Add salary comparison features
- [ ] Support for company reviews and ratings

## Disclaimer

This tool is for educational and personal use only. Ensure you comply with the terms of service of job boards when scraping. Some job boards may have restrictions on automated scraping.

---

**Happy job hunting! 🚀**
