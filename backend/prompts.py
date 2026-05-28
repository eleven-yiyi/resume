"""
Llama prompt templates.
All prompts instruct the model to stay strictly within provided facts.
"""

# ── Preference slot extraction from free-text input ──────────────────────────
PREF_EXTRACT_SYSTEM = """\
You are a job preference extractor. Extract structured fields from the user's message.
Return ONLY valid JSON — no markdown, no explanation.

Schema:
{
  "job_functions": ["Product Management", ...] or null,
  "work_arrangement": "onsite"|"hybrid"|"remote"|"open" or null,
  "location": "city or region string" or null,
  "job_type": "full-time"|"part-time"|"contract"|"internship" or null,
  "salary_min": integer or null,
  "salary_max": integer or null,
  "extra_notes": ["soft constraint string", ...]
}

Rules:
- extra_notes captures anything that doesn't fit the above slots (e.g. "no startup", "must have visa sponsor")
- If a field is not mentioned, set it to null (extra_notes defaults to [])
- Salary numbers should be monthly unless user specifies otherwise
"""

def pref_extract_messages(user_input: str) -> list[dict]:
    return [
        {"role": "system", "content": PREF_EXTRACT_SYSTEM},
        {"role": "user", "content": user_input},
    ]


# ── Resume parsing: extract structured facts ────────────────────────────────
RESUME_PARSE_SYSTEM = """\
You are a resume parser. Extract structured facts from the resume text.
Return ONLY valid JSON — no markdown, no explanation.

Schema:
{
  "name": "string",
  "email": "string or null",
  "location": "string or null",
  "years_of_experience": number or null,
  "education": [{"degree": "string", "school": "string", "year": "string or null"}],
  "work_experience": [
    {"title": "string", "company": "string", "duration": "string", "bullets": ["string"]}
  ],
  "skills": ["string"],
  "languages": ["string"],
  "summary": "string or null"
}

Rules:
- Only extract facts explicitly stated in the text
- Do NOT invent or infer skills not mentioned
- years_of_experience: sum of work history duration if calculable, else null
"""

def resume_parse_messages(raw_text: str) -> list[dict]:
    return [
        {"role": "system", "content": RESUME_PARSE_SYSTEM},
        {"role": "user", "content": f"Parse this resume:\n\n{raw_text[:6000]}"},
    ]


# ── "Why it fits you" generation ─────────────────────────────────────────────
WHY_FIT_SYSTEM = """\
You are a career advisor. Given a candidate's resume facts and a job description,
write 2-3 bullet points explaining why this role fits them.

Rules:
- Be specific: reference actual skills, experience, or preferences from the data
- NEVER mention skills or experience not present in the resume_facts
- Each bullet under 70 characters
- Return ONLY a JSON array of strings, e.g. ["reason 1", "reason 2"]
"""

def why_fit_messages(resume_facts: dict, jd: dict, preferences: dict) -> list[dict]:
    context = f"""
Resume facts: {resume_facts}

Job: {jd['title']} at {jd['company']} ({jd['location']})
Description: {jd['description'][:1500]}

Candidate preferences:
- Job functions: {preferences.get('job_functions')}
- Work arrangement: {preferences.get('work_arrangement')}
- Location: {preferences.get('location')}
- Salary range: {preferences.get('salary_min')}–{preferences.get('salary_max')} {jd.get('currency','SGD')}/mo
"""
    return [
        {"role": "system", "content": WHY_FIT_SYSTEM},
        {"role": "user", "content": context},
    ]
