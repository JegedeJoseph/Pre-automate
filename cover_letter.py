# cover_letter.py
import httpx, os, asyncio

ZAIN_RESUME_SUMMARY = """
Senior Software Engineer with 10+ years of experience. Currently at Google as Senior SWE.
Led a 7-engineer team building GCP-native FP&A platform with multi-agent orchestration
(Google ADK, Vertex AI), automating 40% of financial workflows. Built LLM-powered SQL 
query assistant boosting analytics speed by 40%. Previously Lead SWE at Lifion by ADP 
serving 1M+ employees, achieving 99.99% uptime, designing Kafka-based distributed cache 
(67% latency reduction). Early engineer at Warren Brasil fintech startup. MS Computer 
Engineering, NYU. Expert in Python, Java, TypeScript, GCP, AWS, LLMs, distributed 
systems, Kubernetes, Kafka, Angular, React.
"""

async def generate_cover_letter(job: dict) -> str:
    prompt = f"""You are writing a cover letter for Zain Malik, a Senior Software Engineer
with 10+ years of experience applying to: {job['title']} at {job['company']}.

Zain's background:
{ZAIN_RESUME_SUMMARY}

Write a concise, compelling 3-paragraph cover letter (under 200 words). 
- Para 1: Why this specific role at this company excites Zain
- Para 2: His most relevant achievement matching this role
- Para 3: Brief close with call to action
Do not use generic phrases. Be specific. Do not use "I am writing to apply".
Output ONLY the letter text, no subject line."""

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",  # free tier / cheapest
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        data = r.json()
        return data["content"][0]["text"]

async def generate_all_letters(jobs: list[dict]) -> dict:
    """Returns {job_id: cover_letter_text}"""
    tasks = [generate_cover_letter(j) for j in jobs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    letters = {}
    for job, result in zip(jobs, results):
        if isinstance(result, str):
            letters[job["job_id"]] = result
        else:
            letters[job["job_id"]] = ""
    return letters