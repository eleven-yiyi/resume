"""
Seed script: import Southeast Asia job descriptions into DB.
Run: python scripts/import_jds.py

Generates embeddings locally and inserts all JDs.
"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from services.llama import embed

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://boss:boss123@localhost:5432/bossjob")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# ── JD data — add your real entries here following the same structure ─────────
# work_arrangement: "onsite" | "hybrid" | "remote"
# job_type:         "full-time" | "part-time" | "contract" | "internship"
# currency:         "SGD" | "MYR" | "IDR" | "PHP" | "THB" | "USD" | ...
# highlights:       3–5 short bullet strings shown on the match card
# tags:             skill/domain keywords used for embedding quality
JDS = [
    {
        "title": "Example Title",
        "company": "Example Company",
        "location": "Singapore",
        "work_arrangement": "hybrid",
        "job_type": "full-time",
        "salary_min": 5000, "salary_max": 8000, "currency": "SGD",
        "description": "Full job description text goes here.",
        "highlights": ["Highlight 1", "Highlight 2", "Highlight 3"],
        "tags": ["tag1", "tag2", "tag3"],
    },
    # ... add up to ~100 entries
]


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    print(f"Importing {len(JDS)} JDs...")

    async with engine.begin() as conn:
        for i, jd in enumerate(JDS):
            embed_text = f"{jd['title']} {jd['company']} {jd['description']} {' '.join(jd['tags'])}"
            vector = embed(embed_text)

            import json
            await conn.execute(
                text("""
                    INSERT INTO job_descriptions
                        (title, company, location, work_arrangement, job_type,
                         salary_min, salary_max, currency, description,
                         highlights, tags, embedding)
                    VALUES
                        (:title, :company, :location, :wa, :jt,
                         :smin, :smax, :currency, :desc,
                         :highlights, :tags, :embedding)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "title":     jd["title"],
                    "company":   jd["company"],
                    "location":  jd["location"],
                    "wa":        jd["work_arrangement"],
                    "jt":        jd["job_type"],
                    "smin":      jd["salary_min"],
                    "smax":      jd["salary_max"],
                    "currency":  jd["currency"],
                    "desc":      jd["description"],
                    "highlights": json.dumps(jd["highlights"]),
                    "tags":      json.dumps(jd["tags"]),
                    "embedding": str(vector),
                }
            )
            print(f"  [{i+1}/{len(JDS)}] {jd['title']} @ {jd['company']}")

    print("Done.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
