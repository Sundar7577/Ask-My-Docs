#!/usr/bin/env python3
# test_pipeline.py — Quick CLI test of the full RAG pipeline
# Usage: python test_pipeline.py path/to/your.pdf "Your question here"

import sys
import os
from ingest import ingest_pdf, collection_count
from generator import generate_answer


def main():
    if len(sys.argv) < 3:
        print("Usage: python test_pipeline.py <path_to_pdf> <question>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    question = sys.argv[2]

    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("  AskMyDocs — RAG Pipeline Test")
    print(f"{'='*60}\n")

    # 1. Ingest
    print(f"📄 Ingesting: {pdf_path}")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    filename = os.path.basename(pdf_path)
    result   = ingest_pdf(pdf_bytes, filename)

    print(f"   ✅ Pages: {result['pages']} | Chunks stored: {result['chunks']}")
    print(f"   📦 Total chunks in DB: {collection_count()}\n")

    # 2. Retrieve + Generate
    print(f"❓ Question: {question}\n")
    print("🔍 Retrieving relevant chunks...")

    output = generate_answer(question)

    # 3. Show retrieved chunks
    print(f"\n📎 Retrieved {len(output['chunks'])} chunks:\n")
    for i, chunk in enumerate(output["chunks"], 1):
        print(f"  [{i}] Page {chunk['page']} | Score: {chunk['score']:.3f}")
        print(f"      {chunk['text'][:150].strip()}…")
        print()

    # 4. Show answer
    print(f"{'='*60}")
    print("🤖 Gemini Answer:")
    print(f"{'='*60}")
    print(output["answer"])
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
