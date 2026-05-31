# api.py — FastAPI server for AskMyPDF
# Wraps your existing ingest.py, retriever.py, generator.py as HTTP endpoints.
#
# CONCEPT: FastAPI turns your Python functions into a real web API.
# Any frontend, mobile app, or tool can now call your RAG pipeline over HTTP.

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# ── Import YOUR existing modules (nothing changed inside them) ─────────────────
from ingest import ingest_pdf, list_ingested_sources, delete_source, collection_count
from generator import generate_answer

# ─────────────────────────────────────────────────────────────────────────────
# App setup
# CONCEPT: FastAPI() creates your app. The metadata shows up in auto-generated
# docs at /docs (Swagger UI) — free, interactive API docs with zero extra work.
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AskMyPDF API",
    description="Upload PDFs and ask questions using Gemini + ChromaDB RAG pipeline.",
    version="1.0.0",
)

# CONCEPT: CORS middleware lets browsers (your Streamlit UI or any frontend)
# call this API from a different URL. Without this, browsers block the request.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production, replace * with your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response models
# CONCEPT: Pydantic models define the shape of JSON going in and out.
# FastAPI auto-validates them and shows them in /docs. If a field is missing
# or the wrong type, FastAPI returns a clear 422 error automatically.
# ─────────────────────────────────────────────────────────────────────────────
class AskRequest(BaseModel):
    query: str
    source_filter: Optional[list[str]] = None   # limit to specific PDFs
    chat_history: Optional[list[dict]] = None   # for multi-turn chat


class AskResponse(BaseModel):
    answer: str
    sources: list[dict]        # chunks used to answer
    context_used: str


class UploadResponse(BaseModel):
    filename: str
    pages: int
    chunks: int
    message: str


class StatusResponse(BaseModel):
    total_chunks: int
    ingested_files: list[str]


# ─────────────────────────────────────────────────────────────────────────────
# Health check
# CONCEPT: Always have a /health endpoint. Cloud Run pings this to know your
# container is alive. Load balancers use it to route traffic.
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


# ─────────────────────────────────────────────────────────────────────────────
# POST /upload — ingest a PDF
# CONCEPT: UploadFile is FastAPI's type for multipart file uploads.
# We read the raw bytes and pass them to YOUR ingest_pdf() — unchanged.
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()   # async read — doesn't block other requests

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Call YOUR existing ingest pipeline — no changes needed
    result = ingest_pdf(pdf_bytes, file.filename)

    return UploadResponse(
        filename=result["filename"],
        pages=result["pages"],
        chunks=result["chunks"],
        message=f"Successfully ingested '{file.filename}' — {result['chunks']} chunks stored.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /ask — answer a question using the RAG pipeline
# CONCEPT: This is the core endpoint. It calls YOUR generate_answer() which
# already handles retrieve → prompt → Gemini. We just expose it over HTTP.
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    result = generate_answer(
        query=request.query,
        source_filter=request.source_filter,
        chat_history=request.chat_history,
    )

    return AskResponse(
        answer=result["answer"],
        sources=result["chunks"],
        context_used=result["context_used"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /status — see what's in ChromaDB
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/status", response_model=StatusResponse)
def status():
    return StatusResponse(
        total_chunks=collection_count(),
        ingested_files=list_ingested_sources(),
    )


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /delete/{filename} — remove a PDF's chunks from ChromaDB
# ─────────────────────────────────────────────────────────────────────────────
@app.delete("/delete/{filename}")
def delete(filename: str):
    deleted = delete_source(filename)
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"No chunks found for '{filename}'.")
    return {"deleted_chunks": deleted, "filename": filename}