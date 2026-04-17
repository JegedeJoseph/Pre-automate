import os
import json
from typing import List
from googleapiclient.discovery import build
from google.oauth2 import service_account
from src.models import JobListing
from src.utils import setup_logger, Config

logger = setup_logger(__name__)

class SheetsService:
    """Google Sheets integration for exporting job listings"""
    
    def __init__(self):
        self.logger = logger
        self.service = None
        self.sheet_id = Config.SPREADSHEET_ID
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Sheets service"""
        try:
            if not Config.GOOGLE_APPLICATION_CREDENTIALS:
                self.logger.warning("Google credentials not configured")
                return
            
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            creds_data = Config.GOOGLE_APPLICATION_CREDENTIALS
            
            # Check if it's a JSON string or file path
            if creds_data.startswith('{'):
                # It's a JSON string
                creds_dict = json.loads(creds_data)
            else:
                # It's a file path
                with open(creds_data, 'r') as f:
                    creds_dict = json.load(f)
            
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=scopes
            )
            
            self.service = build('sheets', 'v4', credentials=creds)
            self.logger.info("Google Sheets service initialized successfully")
        
        except Exception as e:
            self.logger.error(f"Error initializing Google Sheets service: {e}")
            self.service = None
    
    def append_jobs(self, jobs: List[JobListing], sheet_range: str = "Sheet1!A2"):
        """Append job listings to Google Sheet"""
        if not self.service or not self.sheet_id:
            self.logger.warning("Google Sheets not configured. Skipping export.")
            return False
        
        try:
            # Convert job objects to list of lists
            values = []
            for job in jobs:
                row = [
                    job.title,
                    job.company,
                    job.location,
                    job.link,
                    job.description,
                    job.salary or "",
                    job.job_type or "",
                    ", ".join(job.matched_skills),
                    ", ".join(job.missing_skills),
                    f"{job.match_score:.1f}%",
                    job.source,
                    str(job.scraped_at)
                ]
                values.append(row)
            
            if not values:
                self.logger.info("No jobs to export")
                return True
            
            body = {'values': values}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=sheet_range,
                valueInputOption="RAW",
                body=body
            ).execute()
            
            self.logger.info(f"Successfully exported {len(jobs)} jobs to Google Sheets")
            return True
        
        except Exception as e:
            self.logger.error(f"Error exporting to Google Sheets: {e}")
            return False
    
    def create_headers(self, sheet_name: str = "Sheet1"):
        """Create headers in the sheet"""
        if not self.service or not self.sheet_id:
            return False
        
        try:
            headers = [
                "Job Title",
                "Company",
                "Location",
                "Link",
                "Description",
                "Salary",
                "Job Type",
                "Matched Skills",
                "Missing Skills",
                "Match Score",
                "Source",
                "Scraped Date"
            ]
            
            body = {'values': [headers]}
            
            # Clear existing data first
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.sheet_id,
                range=f"{sheet_name}!A1:L1000"
            ).execute()
            
            # Add headers
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption="RAW",
                body=body
            ).execute()
            
            self.logger.info(f"Headers created in {sheet_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating headers: {e}")
            return False
    
    def clear_sheet(self, sheet_name: str = "Sheet1"):
        """Clear all data from sheet"""
        if not self.service or not self.sheet_id:
            return False
        
        try:
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.sheet_id,
                range=f"{sheet_name}!A1:L10000"
            ).execute()
            
            self.logger.info(f"Cleared {sheet_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error clearing sheet: {e}")
            return False
