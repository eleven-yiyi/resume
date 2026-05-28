"""
Two-stage matching pipeline:
  Stage 1 — SQL hard filter (location, salary, work arrangement, job type)
  Stage 2 — Vector cosine rerank on filtered results
  Stage 3 — Llama generates "why it fits" for top N
"""
import asyncio
from sqlalchemy import text
from services.llama import embed, llama_chat_json
from prompts import why_fit_messages

# Injected from main.py
_db = None

def init_db(engine):
    global _db
    _db = engine


async def search(preferences: dict, resume_facts: dict, top_n: int = 3) -> list[dict]:
    query_text = _build_query_text(resume_facts, preferences)
    query_vec  = embed(query_text)

    async with _db.connect() as conn:
        # Stage 1: hard filter
        rows = await _hard_filter(conn, preferences)
        if not rows:
            # Fallback: skip filters, search all
            rows = await _all_jds(conn)

        # Stage 2: vector rerank
        ranked = _rerank(rows, query_vec)[:top_n]

        # Stage 3: generate "why it fits" in parallel
        results = await asyncio.gather(*[
            _annotate(jd, resume_facts, preferences) for jd in ranked
        ])

    return results


# ── helpers ──────────────────────────────────────────────────────────────────

def _build_query_text(resume_facts: dict, preferences: dict) -> str:
    """Combine resume skills + preferred job functions into a query string."""
    parts = []
    if skills := resume_facts.get("skills"):
        parts.append("Skills: " + ", ".join(skills))
    if summary := resume_facts.get("summary"):
        parts.append(summary)
    if jf := preferences.get("job_functions"):
        parts.append("Looking for: " + ", ".join(jf))
    if notes := preferences.get("extra_notes"):
        parts.extend(notes)
    return " | ".join(parts)


async def _hard_filter(conn, prefs: dict):
    conditions = ["1=1"]
    params = {}

    if wa := prefs.get("work_arrangement"):
        if wa != "open":
            conditions.append("work_arrangement = :wa")
            params["wa"] = wa

    if jt := prefs.get("job_type"):
        conditions.append("job_type = :jt")
        params["jt"] = jt

    if sal_min := prefs.get("salary_min"):
        conditions.append("(salary_max IS NULL OR salary_max >= :sal_min)")
        params["sal_min"] = sal_min

    where = " AND ".join(conditions)
    result = await conn.execute(
        text(f"SELECT * FROM job_descriptions WHERE {where} LIMIT 100"),
        params
    )
    return result.mappings().all()


async def _all_jds(conn):
    result = await conn.execute(text("SELECT * FROM job_descriptions LIMIT 100"))
    return result.mappings().all()


def _cosine(a: list[float], b: list[float]) -> float:
    import numpy as np
    a, b = np.array(a), np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else 0.0


def _rerank(rows, query_vec: list[float]) -> list[dict]:
    scored = []
    for row in rows:
        jd = dict(row)
        jd_vec = jd.get("embedding") or []
        score = _cosine(query_vec, jd_vec) if jd_vec else 0.0
        jd["_score"] = score
        scored.append(jd)
    return sorted(scored, key=lambda x: x["_score"], reverse=True)


async def _annotate(jd: dict, resume_facts: dict, preferences: dict) -> dict:
    try:
        reasons = await llama_chat_json(
            why_fit_messages(resume_facts, jd, preferences)
        )
    except Exception:
        reasons = ["Profile aligns with role requirements"]

    return {
        "id":              str(jd["id"]),
        "title":           jd["title"],
        "company":         jd["company"],
        "location":        jd["location"],
        "work_arrangement": jd["work_arrangement"],
        "salary_min":      jd["salary_min"],
        "salary_max":      jd["salary_max"],
        "currency":        jd["currency"],
        "highlights":      jd["highlights"],
        "tags":            jd["tags"],
        "match_score":     round(jd["_score"] * 100),
        "why_fit":         reasons if isinstance(reasons, list) else [str(reasons)],
    }
