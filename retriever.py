# retriever.py — Semantic retrieval from ChromaDB
# Embeds the user query and finds the most relevant chunks.

from ingest import get_embedder, get_collection
from config import TOP_K


def retrieve(query: str, source_filter: list[str] | None = None, top_k: int = TOP_K) -> list[dict]:
    """
    Embed `query` and return the top-k most similar chunks from ChromaDB.

    Parameters
    ----------
    query         : natural-language question from the user
    source_filter : if provided, restrict search to these source filenames
    top_k         : number of chunks to return

    Returns
    -------
    List of dicts: [{text, source, page, score}, ...]
    """
    embedder   = get_embedder()
    collection = get_collection()

    if collection.count() == 0:
        return []

    query_embedding = embedder.encode([query], show_progress_bar=False).tolist()

    # Build optional where filter
    where = None
    if source_filter and len(source_filter) == 1:
        where = {"source": source_filter[0]}
    elif source_filter and len(source_filter) > 1:
        where = {"source": {"$in": source_filter}}

    results = collection.query(
        query_embeddings = query_embedding,
        n_results        = min(top_k, collection.count()),
        where            = where,
        include          = ["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        # ChromaDB cosine distance → similarity score (0-1, higher = more similar)
        score = round(1 - dist, 4)
        chunks.append(
            {
                "text":   doc,
                "source": meta.get("source", "unknown"),
                "page":   meta.get("page", "?"),
                "score":  score,
            }
        )

    # Sort by descending relevance
    chunks.sort(key=lambda x: x["score"], reverse=True)
    return chunks


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a single context string for the LLM prompt."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Chunk {i} | Source: {chunk['source']} | Page: {chunk['page']} | Score: {chunk['score']}]\n"
            f"{chunk['text']}"
        )
    return "\n\n---\n\n".join(parts)
