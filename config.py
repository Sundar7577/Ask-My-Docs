# config.py — Central configuration for AskMyDocs RAG pipeline

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Gemini LLM ───────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-2.5-flash"          # Free tier model

# ─── Embedding model (local, free) ────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"         # 384-dim, fast & accurate

# ─── ChromaDB ─────────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR = "./chroma_db"            # Local persistence folder
COLLECTION_NAME    = "askmy_docs"

# ─── Chunking ─────────────────────────────────────────────────────────────────
CHUNK_SIZE    = 500     # characters per chunk
CHUNK_OVERLAP = 80      # overlap between consecutive chunks

# ─── Retrieval ─────────────────────────────────────────────────────────────────
TOP_K = 5               # number of chunks to retrieve per query

# ─── Prompting ────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a helpful document assistant. Answer the user's question
using ONLY the context chunks provided below. If the answer is not found in the
context, say "I couldn't find that information in the uploaded documents."

Always be concise, accurate, and cite the source page when possible."""
