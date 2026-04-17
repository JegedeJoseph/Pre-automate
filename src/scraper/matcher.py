from typing import List, Optional
from difflib import SequenceMatcher
from src.models import JobListing, Resume, JobPreferences
from src.utils import setup_logger

logger = setup_logger(__name__)

class SkillMatcher:
    """Match job listings with resume and preferences"""
    
    def __init__(self, resume: Resume, preferences: JobPreferences):
        self.resume = resume
        self.preferences = preferences
        self.logger = logger
    
    def match_job(self, job: JobListing) -> JobListing:
        """Calculate match score for a job listing"""
        
        # Extract skills
        resume_skills = self._normalize_skills(self.resume.get_skill_names())
        resume_exp_skills = self._normalize_skills(self.resume.get_all_experiences_skills())
        all_resume_skills = resume_skills + resume_exp_skills
        job_skills = self._normalize_skills(job.required_skills)
        
        # Match skills
        matched_skills, missing_skills = self._match_skills(all_resume_skills, job_skills)
        job.matched_skills = matched_skills
        job.missing_skills = missing_skills
        
        # Calculate match score
        score = self._calculate_match_score(job, matched_skills, missing_skills)
        job.match_score = score
        
        self.logger.debug(
            f"Matched {job.title} at {job.company}: "
            f"Score={score:.1f}%, Matched={len(matched_skills)}, Missing={len(missing_skills)}"
        )
        
        return job
    
    def filter_jobs(self, jobs: List[JobListing]) -> List[JobListing]:
        """Filter and score jobs based on preferences"""
        filtered_jobs = []
        
        for job in jobs:
            # Score the job
            job = self.match_job(job)
            
            # Apply filters
            if not self._passes_filters(job):
                continue
            
            # Check minimum match score
            if job.match_score < self.preferences.min_match_score:
                continue
            
            filtered_jobs.append(job)
        
        # Sort by match score descending
        filtered_jobs.sort(key=lambda x: x.match_score, reverse=True)
        
        self.logger.info(f"Filtered {len(jobs)} jobs to {len(filtered_jobs)} matches")
        return filtered_jobs
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize skills for comparison"""
        return [skill.lower().strip() for skill in skills]
    
    def _match_skills(self, resume_skills: List[str], job_skills: List[str]):
        """Match resume skills with job requirements"""
        matched = []
        missing = []
        
        resume_skills_normalized = self._normalize_skills(resume_skills)
        job_skills_normalized = self._normalize_skills(job_skills)
        
        for job_skill in job_skills_normalized:
            # Check for exact match
            if job_skill in resume_skills_normalized:
                matched.append(job_skill)
                continue
            
            # Check for partial match (similarity > 80%)
            best_match = None
            best_ratio = 0
            
            for resume_skill in resume_skills_normalized:
                ratio = SequenceMatcher(None, job_skill, resume_skill).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = resume_skill
            
            if best_ratio > 0.8:
                matched.append(job_skill)
            else:
                missing.append(job_skill)
        
        return matched, missing
    
    def _calculate_match_score(self, job: JobListing, matched: List[str], missing: List[str]) -> float:
        """Calculate overall match score"""
        if not job.required_skills:
            base_score = 50.0
        else:
            # Calculate skill match percentage
            skill_match_pct = (len(matched) / len(job.required_skills)) * 100
            base_score = skill_match_pct
        
        # Weight adjustments
        score = base_score
        
        # Bonus for matching title preferences
        if self.preferences.target_titles:
            for target_title in self.preferences.target_titles:
                if self._fuzzy_match(target_title.lower(), job.title.lower(), 0.7):
                    score = min(100, score + 10)
                    break
        
        # Penalty for excluded keywords
        if self.preferences.excluded_keywords:
            job_desc_lower = (job.description + " " + job.title).lower()
            for keyword in self.preferences.excluded_keywords:
                if keyword.lower() in job_desc_lower:
                    score = max(0, score - 20)
                    break
        
        # Penalty for excluded companies
        if job.company in self.preferences.excluded_companies:
            score = max(0, score - 30)
        
        return min(100, max(0, score))
    
    def _passes_filters(self, job: JobListing) -> bool:
        """Check if job passes all preference filters"""
        
        # Check salary range
        if self.preferences.min_salary or self.preferences.max_salary:
            if not self._check_salary_match(job.salary):
                return False
        
        # Check job type
        if job.job_type and self.preferences.job_types:
            if not any(jt.lower() in job.job_type.lower() for jt in self.preferences.job_types):
                return False
        
        # Check location (basic check)
        if self.preferences.locations:
            if not any(loc.lower() in job.location.lower() for loc in self.preferences.locations):
                if self.preferences.remote_preference != "remote_only":
                    return False
        
        # Check remote preference
        if self.preferences.remote_preference == "remote_only":
            if not self._is_remote_job(job.location, job.description):
                return False
        elif self.preferences.remote_preference == "hybrid":
            if not self._is_hybrid_job(job.location, job.description):
                if not self._is_remote_job(job.location, job.description):
                    return False
        
        return True
    
    def _check_salary_match(self, salary_str: Optional[str]) -> bool:
        """Check if salary matches preferences"""
        if not salary_str:
            return True
        
        # Extract numbers from salary string
        import re
        numbers = re.findall(r'\d+,?\d*', salary_str)
        
        if not numbers:
            return True
        
        try:
            salary_values = [int(num.replace(',', '')) for num in numbers]
            avg_salary = sum(salary_values) / len(salary_values)
            
            if self.preferences.min_salary and avg_salary < self.preferences.min_salary:
                return False
            
            if self.preferences.max_salary and avg_salary > self.preferences.max_salary:
                return False
        except (ValueError, ZeroDivisionError):
            return True
        
        return True
    
    def _is_remote_job(self, location: str, description: str) -> bool:
        """Check if job is remote"""
        remote_keywords = ['remote', 'anywhere', 'work from home', 'virtual', 'distributed']
        combined = (location + " " + description).lower()
        return any(keyword in combined for keyword in remote_keywords)
    
    def _is_hybrid_job(self, location: str, description: str) -> bool:
        """Check if job is hybrid"""
        hybrid_keywords = ['hybrid', 'flexible', 'flexible location']
        combined = (location + " " + description).lower()
        return any(keyword in combined for keyword in hybrid_keywords)
    
    def _fuzzy_match(self, str1: str, str2: str, threshold: float) -> bool:
        """Fuzzy string matching"""
        ratio = SequenceMatcher(None, str1, str2).ratio()
        return ratio >= threshold


from typing import Optional
