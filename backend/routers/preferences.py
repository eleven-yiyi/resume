"""
POST /api/preferences/extract   — NLP: free-text → slot JSON
POST /api/preferences/save      — save/upsert preference record
GET  /api/preferences/{resume_id}
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
import json

from services.llama import llama_chat_json
from prompts import pref_extract_messages
from main import engine

router = APIRouter()


class ExtractRequest(BaseModel):
    text: str


class SaveRequest(BaseModel):
    resume_id: str
    job_functions:     list[str]  = []
    work_arrangement:  str | None = None
    location:          str | None = None
    job_type:          str | None = None
    salary_min:        int | None = None
    salary_max:        int | None = None
    salary_negotiable: bool       = False
    extra_notes:       list[str]  = []
    feedback_reasons:  list[dict] = []   # [{jobIdx, reason}, ...]


@router.post("/extract")
async def extract_preferences(req: ExtractRequest):
    """Parse free-text input into structured preference slots."""
    try:
        slots = await llama_chat_json(pref_extract_messages(req.text))
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {e}")
    return slots


@router.post("/save")
async def save_preferences(req: SaveRequest):
    """Upsert preference record for a resume."""
    async with engine.begin() as conn:
        # Check if preference record already exists
        existing = await conn.execute(
            text("SELECT id FROM preferences WHERE resume_id = :rid"),
            {"rid": req.resume_id}
        )
        row = existing.fetchone()

        if row:
            await conn.execute(
                text("""
                    UPDATE preferences SET
                        job_functions     = :jf,
                        work_arrangement  = :wa,
                        location          = :loc,
                        job_type          = :jt,
                        salary_min        = :smin,
                        salary_max        = :smax,
                        salary_negotiable = :neg,
                        extra_notes       = :en,
                        feedback_reasons  = :fr
                    WHERE resume_id = :rid
                """),
                {
                    "jf":  req.job_functions,
                    "wa":  req.work_arrangement,
                    "loc": req.location,
                    "jt":  req.job_type,
                    "smin": req.salary_min,
                    "smax": req.salary_max,
                    "neg": req.salary_negotiable,
                    "en":  json.dumps(req.extra_notes),
                    "fr":  json.dumps(req.feedback_reasons),
                    "rid": req.resume_id,
                }
            )
            pref_id = str(row[0])
        else:
            result = await conn.execute(
                text("""
                    INSERT INTO preferences
                        (resume_id, job_functions, work_arrangement, location,
                         job_type, salary_min, salary_max, salary_negotiable,
                         extra_notes, feedback_reasons)
                    VALUES
                        (:rid, :jf, :wa, :loc, :jt, :smin, :smax, :neg, :en, :fr)
                    RETURNING id
                """),
                {
                    "rid": req.resume_id,
                    "jf":  req.job_functions,
                    "wa":  req.work_arrangement,
                    "loc": req.location,
                    "jt":  req.job_type,
                    "smin": req.salary_min,
                    "smax": req.salary_max,
                    "neg": req.salary_negotiable,
                    "en":  json.dumps(req.extra_notes),
                    "fr":  json.dumps(req.feedback_reasons),
                }
            )
            pref_id = str(result.scalar())

    return {"preference_id": pref_id}


@router.get("/{resume_id}")
async def get_preferences(resume_id: str):
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT * FROM preferences WHERE resume_id = :rid"),
            {"rid": resume_id}
        )
        row = result.mappings().fetchone()
        if not row:
            raise HTTPException(404, "Preferences not found")
        return dict(row)
