import os
from dotenv import load_dotenv
import json

load_dotenv()

class Config:
    """Configuration manager"""
    
    # Google Sheets
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    
    # Scraper settings
    HEADLESS_BROWSER = os.getenv('HEADLESS_BROWSER', 'true').lower() == 'true'
    BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', '30000'))
    WAIT_TIME = int(os.getenv('WAIT_TIME', '10000'))
    
    # Job search defaults
    DEFAULT_PAGES_TO_SCRAPE = int(os.getenv('DEFAULT_PAGES_TO_SCRAPE', '3'))
    
    # Resume file
    RESUME_FILE_PATH = os.getenv('RESUME_FILE_PATH', './resume/my_resume.pdf')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/app.log')
    
    @staticmethod
    def validate_google_creds():
        """Validate Google credentials"""
        if Config.GOOGLE_APPLICATION_CREDENTIALS:
            try:
                creds_path = Config.GOOGLE_APPLICATION_CREDENTIALS
                if creds_path.startswith('{'):
                    # It's a JSON string
                    json.loads(creds_path)
                else:
                    # It's a file path
                    if not os.path.exists(creds_path):
                        raise FileNotFoundError(f"Credentials file not found: {creds_path}")
                return True
            except Exception as e:
                print(f"Warning: Invalid Google credentials: {e}")
                return False
        return False
