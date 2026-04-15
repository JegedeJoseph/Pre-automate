# scorer.py
import re

ZAIN_KEYWORDS = [
    "gcp", "aws", "azure", "python", "java", "typescript", "javascript",
    "llm", "vertex ai", "google adk", "multi-agent", "agent", "generative ai",
    "kafka", "kubernetes", "bigquery", "spanner", "pub/sub", "pubsub",
    "angular", "react", "node.js", "nodejs", "spring boot",
    "elasticsearch", "redis", "mongodb", "docker", "ci/cd",
    "rest api", "graphql", "microservices", "distributed systems",
    "datadog", "django", "flask", "next.js", "nextjs",
    "ml", "machine learning", "nlp", "openai", "gemini",
    "cloud native", "full stack", "fullstack", "backend"
]

TARGET_TITLES = [
    "senior software engineer", "software engineer",
    "ai engineer", "machine learning engineer", "ml engineer",
    "backend engineer", "full stack engineer", "fullstack engineer",
    "staff engineer", "principal engineer", "lead engineer"
]

SENIORITY_SIGNALS = ["senior", "sr.", "lead", "staff", "principal", "head of", "architect"]

SALARY_FLOOR = 140_000

def parse_salary(salary_str: str) -> int | None:
    """Extract lowest salary number from string like '$140k–$180k' or '$160,000'."""
    if not salary_str:
        return None
    nums = re.findall(r"\$?([\d,]+)k?", salary_str.lower())
    parsed = []
    for n in nums:
        n = n.replace(",", "")
        val = int(n) * 1000 if int(n) < 1000 else int(n)
        parsed.append(val)
    return min(parsed) if parsed else None

def score_job(job: dict) -> dict:
    title = job.get("title", "").lower()
    description = job.get("description", "").lower()
    salary_str = job.get("salary", "")
    location = job.get("location", "").lower()
    combined_text = f"{title} {description}"
    score = 0
    matched_keywords = []

    # --- Keyword match (35 pts) ---
    for kw in ZAIN_KEYWORDS:
        if kw in combined_text:
            matched_keywords.append(kw)
    keyword_score = min(35, int((len(matched_keywords) / len(ZAIN_KEYWORDS)) * 35 * 3))
    score += keyword_score

    # --- Title match (20 pts) ---
    title_score = 0
    for t in TARGET_TITLES:
        if t in title:
            title_score = 20
            break
    score += title_score

    # --- Salary filter (20 pts) ---
    salary_score = 0
    parsed_sal = parse_salary(salary_str)
    if parsed_sal is None:
        salary_score = 10  # unknown salary: partial credit
    elif parsed_sal >= SALARY_FLOOR:
        salary_score = 20
    score += salary_score

    # --- Remote USA/Canada (15 pts) ---
    location_score = 0
    if any(x in location for x in ["remote", "usa", "us", "united states", "canada", "ca"]):
        location_score = 15
    score += location_score

    # --- Seniority fit (10 pts) ---
    seniority_score = 0
    for s in SENIORITY_SIGNALS:
        if s in title:
            seniority_score = 10
            break
    score += seniority_score

    job["match_score"] = min(score, 100)
    job["keywords_matched"] = ", ".join(matched_keywords[:10])
    return job

def filter_and_score(jobs: list[dict], threshold: int = 60) -> list[dict]:
    scored = [score_job(j) for j in jobs]
    qualified = [j for j in scored if j["match_score"] >= threshold]
    qualified.sort(key=lambda x: x["match_score"], reverse=True)
    return qualified

def deduplicate(jobs: list[dict], seen_ids: set) -> list[dict]:
    new_jobs = []
    for job in jobs:
        if job["job_id"] not in seen_ids:
            new_jobs.append(job)
            seen_ids.add(job["job_id"])
    return new_jobs