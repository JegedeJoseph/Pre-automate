import os
from typing import List, Optional
from src.models import Resume, Skills, WorkExperience
from src.utils import setup_logger
import re

logger = setup_logger(__name__)

class ResumeParser:
    """Parse resume files to extract information"""
    
    COMMON_SKILL_KEYWORDS = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'csharp', 'cpp', 'golang', 'rust',
        'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab',
        # Web Technologies
        'html', 'css', 'react', 'vue', 'angular', 'nodejs', 'express', 'django', 'flask',
        'fastapi', 'spring', 'asp.net', 'laravel', 'rails',
        # Databases
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'firebase',
        'dynamodb', 'cassandra', 'oracle',
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'circleci',
        'gitlab', 'github', 'git', 'ci/cd',
        # Data & Analytics
        'pandas', 'numpy', 'scipy', 'scikit-learn', 'tensorflow', 'pytorch', 'spark',
        'hadoop', 'sql', 'tableau', 'powerbi', 'looker',
        # Tools & Platforms
        'linux', 'windows', 'macos', 'jira', 'confluence', 'slack', 'trello', 'asana',
        'figma', 'xd', 'sketch',
        # Soft Skills
        'leadership', 'communication', 'teamwork', 'project management', 'agile', 'scrum',
        'problem solving', 'analytical', 'strategic thinking'
    ]
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.logger = logger
    
    def parse(self) -> Optional[Resume]:
        """Parse resume file"""
        if not os.path.exists(self.file_path):
            self.logger.error(f"Resume file not found: {self.file_path}")
            return None
        
        file_ext = os.path.splitext(self.file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self._parse_pdf()
        elif file_ext == '.txt':
            return self._parse_text()
        else:
            self.logger.warning(f"Unsupported file format: {file_ext}")
            return self._parse_text()  # Try parsing as text
    
    def _parse_pdf(self) -> Optional[Resume]:
        """Parse PDF resume"""
        try:
            import PyPDF2
            with open(self.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            return self._extract_resume_data(text)
        except ImportError:
            self.logger.warning("PyPDF2 not installed. Attempting text extraction...")
            return self._parse_text()
        except Exception as e:
            self.logger.error(f"Error parsing PDF: {e}")
            return None
    
    def _parse_text(self) -> Optional[Resume]:
        """Parse text resume"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return self._extract_resume_data(text)
        except Exception as e:
            self.logger.error(f"Error parsing text file: {e}")
            return None
    
    def _extract_resume_data(self, text: str) -> Resume:
        """Extract resume data from text"""
        lines = text.split('\n')
        
        # Extract basic info
        name = self._extract_name(lines)
        email = self._extract_email(text)
        phone = self._extract_phone(text)
        location = self._extract_location(lines)
        
        # Extract skills
        skills = self._extract_skills(text)
        
        # Extract work experience
        experience = self._extract_experience(text)
        
        # Extract education
        education = self._extract_education(text)
        
        resume = Resume(
            name=name,
            email=email,
            phone=phone,
            location=location,
            skills=skills,
            experience=experience,
            education=education,
            file_path=self.file_path
        )
        
        self.logger.info(f"Successfully parsed resume: {name}")
        return resume
    
    def _extract_name(self, lines: List[str]) -> str:
        """Extract name from resume"""
        for line in lines[:10]:  # Check first 10 lines
            if line.strip() and len(line.strip().split()) <= 3:
                return line.strip()
        return "Unknown"
    
    def _extract_email(self, text: str) -> str:
        """Extract email from resume"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from resume"""
        phone_pattern = r'\+?1?\s*\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else None
    
    def _extract_location(self, lines: List[str]) -> Optional[str]:
        """Extract location from resume"""
        location_pattern = r'[A-Z][a-z]+,\s*[A-Z]{2}|\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        for line in lines[:15]:
            match = re.search(location_pattern, line)
            if match:
                return match.group(0)
        return None
    
    def _extract_skills(self, text: str) -> List[Skills]:
        """Extract skills from resume"""
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.COMMON_SKILL_KEYWORDS:
            if skill in text_lower:
                found_skills.add(skill)
        
        # Convert to Skills objects
        skills_list = [Skills(name=skill) for skill in sorted(found_skills)]
        return skills_list
    
    def _extract_experience(self, text: str) -> List[WorkExperience]:
        """Extract work experience from resume"""
        experiences = []
        
        # Simple pattern matching for job titles and companies
        # This is a basic implementation - can be enhanced with NLP
        
        job_section_pattern = r'(?:job title|position|title):\s*(.+?)\n.*?(?:company|organization):\s*(.+?)\n'
        matches = re.finditer(job_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            exp = WorkExperience(
                job_title=match.group(1).strip(),
                company=match.group(2).strip()
            )
            experiences.append(exp)
        
        return experiences
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education from resume"""
        education = []
        
        education_keywords = ['degree', 'bachelor', 'master', 'phd', 'diploma', 'certificate']
        lines = text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in education_keywords):
                education.append(line.strip())
        
        return education
