import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

def _make_url() -> str:
    url = os.getenv("DATABASE_URL", "postgresql+asyncpg://boss:boss123@localhost:5432/bossjob")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

engine: AsyncEngine = create_async_engine(_make_url(), echo=False)
