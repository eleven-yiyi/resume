"""
Llama API client — assumes OpenAI-compatible endpoint (Ollama / vLLM / etc.)
"""
import json
import os
import httpx
from functools import lru_cache
from sentence_transformers import SentenceTransformer

LLAMA_BASE_URL = os.getenv("LLAMA_BASE_URL", "http://localhost:11434")
LLAMA_MODEL    = os.getenv("LLAMA_MODEL", "llama3.1")
LLAMA_API_KEY  = os.getenv("LLAMA_API_KEY", "")
EMBED_MODEL    = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def _embed_model() -> SentenceTransformer:
    return SentenceTransformer(EMBED_MODEL)


async def llama_chat(messages: list[dict], temperature: float = 0.2) -> str:
    """Call Llama chat endpoint, return response text."""
    headers = {}
    if LLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {LLAMA_API_KEY}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{LLAMA_BASE_URL}/v1/chat/completions",
            headers=headers,
            json={"model": LLAMA_MODEL, "messages": messages, "temperature": temperature},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def llama_chat_json(messages: list[dict]) -> dict | list:
    """Call Llama and parse response as JSON. Raises ValueError on bad JSON."""
    text = await llama_chat(messages, temperature=0.1)
    # Strip markdown code fences if present
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def embed(text: str) -> list[float]:
    """Embed text locally using sentence-transformers (384 dims)."""
    model = _embed_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()
