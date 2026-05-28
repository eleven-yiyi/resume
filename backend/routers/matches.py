"""
POST /api/matches/search    — run matching pipeline, return top N jobs
POST /api/matches/feedback  — store like/dislike signal
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
import json

from services import matcher
from main import engine

router = APIRouter()


class SearchRequest(BaseModel):
    resume_id:   str
    top_n:       int = 3


class FeedbackRequest(BaseModel):
    resume_id: str
    jd_id:     str
    action:    str          # "like" | "dislike"
    reason:    str | None = None


@router.post("/search")
async def search_matches(req: SearchRequest):
    # Load resume facts
    async with engine.connect() as conn:
        r = await conn.execute(
            text("SELECT parsed_json FROM resumes WHERE id = :id"),
            {"id": req.resume_id}
        )
        resume_row = r.fetchone()
        if not resume_row:
            raise HTTPException(404, "Resume not found")

        p = await conn.execute(
            text("SELECT * FROM preferences WHERE resume_id = :id"),
            {"id": req.resume_id}
        )
        pref_row = p.mappings().fetchone()

    resume_facts = resume_row[0] if isinstance(resume_row[0], dict) else json.loads(resume_row[0])
    preferences  = dict(pref_row) if pref_row else {}

    results = await matcher.search(preferences, resume_facts, top_n=req.top_n)
    return {"matches": results}


@router.post("/feedback")
async def store_feedback(req: FeedbackRequest):
    if req.action not in ("like", "dislike"):
        raise HTTPException(400, "action must be 'like' or 'dislike'")

    async with engine.begin() as conn:
        await conn.execute(
            text("""
                INSERT INTO match_feedback (resume_id, jd_id, action, reason)
                VALUES (:rid, :jid, :action, :reason)
            """),
            {
                "rid":    req.resume_id,
                "jid":    req.jd_id,
                "action": req.action,
                "reason": req.reason,
            }
        )

        # Append dislike reason to preferences.feedback_reasons
        if req.action == "dislike" and req.reason:
            await conn.execute(
                text("""
                    UPDATE preferences
                    SET feedback_reasons = feedback_reasons || :entry::jsonb
                    WHERE resume_id = :rid
                """),
                {
                    "entry": json.dumps([{"jd_id": req.jd_id, "reason": req.reason}]),
                    "rid":   req.resume_id,
                }
            )

    return {"status": "ok"}
