# ingest.py — PDF ingestion pipeline
# Loads PDFs → chunks text → embeds with SentenceTransformer → stores in ChromaDB

import fitz  # PyMuPDF
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
import hashlib
import os


# ─── Singleton helpers ────────────────────────────────────────────────────────

_embedder   = None
_chroma_col = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder


def get_collection() -> chromadb.Collection:
    global _chroma_col
    if _chroma_col is None:
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        _chroma_col = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _chroma_col


# ─── PDF → raw text per page ──────────────────────────────────────────────────

def extract_pages(pdf_bytes: bytes) -> list[dict]:
    """Return a list of {page: int, text: str} dicts from raw PDF bytes."""
    doc   = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    return pages


# ─── Text → overlapping chunks ────────────────────────────────────────────────

def chunk_text(text: str, source: str, page: int) -> list[dict]:
    """Split text into overlapping character-level chunks with metadata."""
    chunks = []
    start  = 0
    idx    = 0
    while start < len(text):
        end   = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(
                {
                    "text":   chunk,
                    "source": source,
                    "page":   page,
                    "idx":    idx,
                }
            )
            idx += 1
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


# ─── Deterministic chunk ID ───────────────────────────────────────────────────

def make_chunk_id(source: str, page: int, idx: int) -> str:
    raw = f"{source}::page{page}::chunk{idx}"
    return hashlib.md5(raw.encode()).hexdigest()


# ─── Main ingestion entry-point ───────────────────────────────────────────────

def ingest_pdf(pdf_bytes: bytes, filename: str) -> dict:
    """
    Full pipeline: PDF bytes → ChromaDB.
    Returns a summary dict with counts.
    """
    pages      = extract_pages(pdf_bytes)
    all_chunks = []

    for page_data in pages:
        chunks = chunk_text(page_data["text"], filename, page_data["page"])
        all_chunks.extend(chunks)

    if not all_chunks:
        return {"filename": filename, "pages": 0, "chunks": 0}

    # Embed all chunks in one batch (fast)
    embedder   = get_embedder()
    texts      = [c["text"] for c in all_chunks]
    embeddings = embedder.encode(texts, show_progress_bar=False).tolist()

    # Prepare ChromaDB inputs
    ids        = [make_chunk_id(c["source"], c["page"], c["idx"]) for c in all_chunks]
    metadatas  = [{"source": c["source"], "page": c["page"]} for c in all_chunks]

    collection = get_collection()

    # Upsert so re-uploading same file is safe
    collection.upsert(
        ids        = ids,
        embeddings = embeddings,
        documents  = texts,
        metadatas  = metadatas,
    )

    return {
        "filename": filename,
        "pages":    len(pages),
        "chunks":   len(all_chunks),
    }


def list_ingested_sources() -> list[str]:
    """Return distinct filenames already in the collection."""
    col = get_collection()
    if col.count() == 0:
        return []
    result  = col.get(include=["metadatas"])
    sources = sorted({m["source"] for m in result["metadatas"]})
    return sources


def delete_source(filename: str) -> int:
    """Delete all chunks from a specific source file. Returns deleted count."""
    col    = get_collection()
    result = col.get(where={"source": filename}, include=["metadatas"])
    ids    = result["ids"]
    if ids:
        col.delete(ids=ids)
    return len(ids)


def collection_count() -> int:
    return get_collection().count()
