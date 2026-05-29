# generator.py — LLM answer generation using Google Gemini
# Takes retrieved context chunks and a user query → returns a grounded answer.

import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT
from retriever import retrieve, format_context


# Configure Gemini once
genai.configure(api_key=GEMINI_API_KEY)


def build_prompt(query: str, context: str) -> str:
    """Assemble the full prompt with system instructions + context + question."""
    return f"""{SYSTEM_PROMPT}

=== CONTEXT FROM DOCUMENTS ===
{context}

=== USER QUESTION ===
{query}

=== YOUR ANSWER ==="""


def generate_answer(
    query: str,
    source_filter: list[str] | None = None,
    chat_history: list[dict] | None = None,
) -> dict:
    """
    Full RAG pipeline: retrieve → prompt → generate.

    Parameters
    ----------
    query         : user's question
    source_filter : limit retrieval to specific files
    chat_history  : list of {role, content} dicts for multi-turn context

    Returns
    -------
    dict with keys: answer, chunks, context_used
    """
    # 1. Retrieve relevant chunks
    chunks = retrieve(query, source_filter=source_filter)

    if not chunks:
        return {
            "answer":       "No documents are indexed yet. Please upload a PDF first.",
            "chunks":       [],
            "context_used": "",
        }

    # 2. Format context
    context = format_context(chunks)

    # 3. Build prompt
    prompt = build_prompt(query, context)

    # 4. Optionally include chat history for multi-turn awareness
    model = genai.GenerativeModel(GEMINI_MODEL)

    if chat_history:
        # Convert our history format to Gemini's format
        gemini_history = []
        for msg in chat_history[:-1]:   # exclude the current question
            role    = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat   = model.start_chat(history=gemini_history)
        result = chat.send_message(prompt)
    else:
        result = model.generate_content(prompt)

    answer = result.text.strip()

    return {
        "answer":       answer,
        "chunks":       chunks,
        "context_used": context,
    }
