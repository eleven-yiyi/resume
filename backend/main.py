from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()

from routers import resume, preferences, matches
from services import matcher

app = FastAPI(title="BossJob AI Demo", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://boss:boss123@localhost:5432/bossjob")
# asyncpg needs postgresql+asyncpg scheme
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)

@app.on_event("startup")
async def startup():
    matcher.init_db(engine)

app.include_router(resume.router,      prefix="/api/resume",      tags=["resume"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["preferences"])
app.include_router(matches.router,     prefix="/api/matches",     tags=["matches"])

@app.get("/health")
async def health():
    return {"status": "ok"}
