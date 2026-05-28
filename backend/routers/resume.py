"""
POST /api/resume/parse
  - Accepts PDF upload
  - Extracts text (pypdf for native, PaddleOCR for scanned)
  - Calls Llama to parse into structured JSON
  - Stores in DB, returns resume_id + parsed_json
"""
import io
from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy import text
from pypdf import PdfReader

from database import engine
from services.llama import llama_chat_json
from prompts import resume_parse_messages

router = APIRouter()

MAX_PAGES = 5


def _extract_text_native(file_bytes: bytes) -> tuple[str, float]:
    """Extract text from native PDF. Returns (text, confidence)."""
    reader = PdfReader(io.BytesIO(file_bytes))
    if len(reader.pages) > MAX_PAGES:
        raise HTTPException(400, f"Resume must be {MAX_PAGES} pages or fewer.")
    pages = [p.extract_text() or "" for p in reader.pages]
    text = "\n".join(pages).strip()
    confidence = 1.0 if len(text) > 100 else 0.0
    return text, confidence


def _extract_text_ocr(file_bytes: bytes) -> tuple[str, float]:
    """Extract text via PaddleOCR for scanned PDFs."""
    try:
        from paddleocr import PaddleOCR
        import numpy as np
        from PIL import Image
        import fitz  # PyMuPDF

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if doc.page_count > MAX_PAGES:
            raise HTTPException(400, f"Resume must be {MAX_PAGES} pages or fewer.")

        ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        lines, scores = [], []
        for page in doc:
            pix = page.get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            result = ocr.ocr(np.array(img), cls=True)
            for block in (result or []):
                for line in (block or []):
                    lines.append(line[1][0])
                    scores.append(line[1][1])

        avg_conf = sum(scores) / len(scores) if scores else 0.0
        return "\n".join(lines), avg_conf
    except ImportError:
        raise HTTPException(500, "OCR dependencies not installed.")


@router.post("/parse")
async def parse_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")

    file_bytes = await file.read()

    # Try native extraction first
    raw_text, confidence = _extract_text_native(file_bytes)

    ocr_warning = False
    if confidence < 0.85:
        # Scanned PDF — fall back to OCR
        raw_text, confidence = _extract_text_ocr(file_bytes)
        ocr_warning = confidence < 0.85

    if not raw_text.strip():
        raise HTTPException(422, "Could not extract text from this PDF.")

    # Parse with Llama
    try:
        parsed = await llama_chat_json(resume_parse_messages(raw_text))
    except Exception as e:
        raise HTTPException(500, f"Resume parsing failed: {e}")

    # Persist
    async with engine.begin() as conn:
        row = await conn.execute(
            text("INSERT INTO resumes (raw_text, parsed_json) VALUES (:t, :j) RETURNING id"),
            {"t": raw_text, "j": parsed if isinstance(parsed, str) else str(parsed)},
        )
        resume_id = str(row.scalar())

    return {
        "resume_id":   resume_id,
        "parsed":      parsed,
        "ocr_warning": ocr_warning,
        "confidence":  round(confidence, 2),
    }
