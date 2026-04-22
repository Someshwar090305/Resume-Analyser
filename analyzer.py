import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def _call(prompt):
    completion = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2048,
    )
    raw = completion.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def extract_resume_info(resume_text):
    prompt = (
        "You are a professional resume parser. "
        "Return ONLY valid JSON matching this exact schema — no markdown, no preamble, no explanation:\n"
        "{\n"
        '  "name": "Full Name",\n'
        '  "contact": { "email": "...", "phone": "...", "linkedin": "..." },\n'
        '  "skills": ["Python", "SQL", "Machine Learning"],\n'
        '  "experience": [\n'
        '    { "title": "...", "company": "...", "duration": "...", "highlights": ["..."] }\n'
        "  ],\n"
        '  "education": [\n'
        '    { "degree": "...", "institution": "...", "year": "..." }\n'
        "  ],\n"
        '  "summary": "2-sentence professional profile"\n'
        "}\n\n"
        "RESUME:\n---\n"
        f"{resume_text}\n---"
    )
    return _call(prompt)


def extract_job_requirements(jd_text):
    prompt = (
        "You are a professional job description analyst. "
        "Your task is to extract EVERY skill, technology, tool, language, and framework mentioned anywhere in the job description — "
        "including inside sections labelled 'Required', 'Preferred', 'Nice to Have', 'Technologies', 'Qualifications', 'Responsibilities', or anywhere else. "
        "Do NOT miss any skill. Be exhaustive.\n\n"
        "Classify skills as follows:\n"
        "- required_skills: skills listed under Required/Must-Have/Qualifications OR mentioned as proficiency/knowledge requirements\n"
        "- preferred_skills: skills listed under Preferred/Nice-to-Have/Bonus sections\n\n"
        "Return ONLY valid JSON matching this exact schema — no markdown, no preamble, no explanation:\n"
        "{\n"
        '  "role": "Job Title",\n'
        '  "required_skills": ["Python", "Java", "JavaScript", "SQL", "PostgreSQL", "Git", "HTML", "CSS"],\n'
        '  "preferred_skills": ["AWS", "Azure", "Docker", "Kubernetes", "RESTful APIs", "Microservices"],\n'
        '  "experience_years": "1-3 years",\n'
        '  "summary": "1-sentence role description"\n'
        "}\n\n"
        "JOB DESCRIPTION:\n---\n"
        f"{jd_text}\n---"
    )
    return _call(prompt)


def match_and_score(resume_dict, jd_dict):
    prompt = (
        "You are an expert ATS analyst. "
        "Match skills semantically: ML = Machine Learning, JS = JavaScript, NLP = Natural Language Processing. "
        "A skill counts as matched if the resume demonstrates it even if the exact keyword differs. "
        "Return ONLY valid JSON matching this exact schema — no markdown, no preamble, no explanation:\n"
        "{\n"
        '  "score": 78,\n'
        '  "matched_skills": ["Python", "SQL", "Machine Learning"],\n'
        '  "missing_skills": ["AWS", "Docker", "Kubernetes"],\n'
        '  "suggestions": [\n'
        '    "Add a dedicated Skills section listing AWS and Docker explicitly.",\n'
        '    "Quantify your ML project results with metrics.",\n'
        '    "Mention any cloud deployment experience."\n'
        "  ]\n"
        "}\n\n"
        "score must be an integer 0-100. Provide exactly 3-5 specific, actionable suggestions.\n\n"
        "RESUME JSON:\n---\n"
        f"{json.dumps(resume_dict, indent=2)}\n---\n\n"
        "JOB DESCRIPTION JSON:\n---\n"
        f"{json.dumps(jd_dict, indent=2)}\n---"
    )
    return _call(prompt)
