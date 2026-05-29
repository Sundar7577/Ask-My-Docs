# 📚 AskMyDocs — RAG System

> **Chat with your PDF documents** using Retrieval-Augmented Generation.
> Built with Sentence Transformers + ChromaDB + Google Gemini — **100% free stack.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-orange?style=flat)
![Gemini](https://img.shields.io/badge/Gemini-2.5--flash-4285F4?style=flat&logo=google&logoColor=white)

---

## 🏗️ Architecture

```
PDF Upload
    │
    ▼
┌─────────────────────────────────────────────┐
│              INGESTION PIPELINE             │
│                                             │
│  PyMuPDF         →  Text Chunks (500 chars, │
│  (extract text)     80 overlap)             │
│                         │                  │
│                         ▼                  │
│              Sentence Transformers          │
│              (all-MiniLM-L6-v2 embeddings) │
│                         │                  │
│                         ▼                  │
│              ChromaDB (local persistence)  │
└─────────────────────────────────────────────┘
                          │
                     [stored]
                          │
User Query                │
    │                     │
    ▼                     ▼
┌─────────────────────────────────────────────┐
│               QUERY PIPELINE                │
│                                             │
│  Embed Query  →  Cosine Similarity Search   │
│                  (Top-5 chunks from Chroma) │
│                         │                  │
│                         ▼                  │
│         Prompt = System + Context + Query  │
│                         │                  │
│                         ▼                  │
│              Google Gemini 2.5 Flash        │
│              (Free tier LLM)               │
│                         │                  │
│                         ▼                  │
│         Answer + Source Citations           │
└─────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Details |
|---|---|
| 📄 Multi-PDF support | Upload and index multiple PDFs simultaneously |
| 🔍 Semantic search | Cosine similarity over dense embeddings |
| 💬 Multi-turn chat | Conversation history passed to Gemini |
| 📎 Source citations | See exactly which chunk + page answered your question |
| 📊 Relevance scores | Each retrieved chunk shows a similarity score |
| 🗂️ Scope filter | Restrict Q&A to specific uploaded documents |
| 🗑️ Document management | Delete individual documents from the index |
| 💾 Persistent storage | ChromaDB persists across sessions |

---

## 🚀 Quick Start

### 1. Clone / download
```bash
git clone https://github.com/yourname/askmy-docs.git
cd askmy-docs
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Gemini API key
```bash
cp .env.example .env
# Edit .env and paste your key from https://aistudio.google.com
```

### 4. Run the app
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🧪 CLI Test (no UI needed)

```bash
python test_pipeline.py path/to/your.pdf "What is this document about?"
```

---

## 📁 Project Structure

```
askmy-docs/
├── app.py              # Streamlit UI — chat interface
├── ingest.py           # PDF → chunks → embeddings → ChromaDB
├── retriever.py        # Query embedding + ChromaDB similarity search
├── generator.py        # Gemini LLM answer generation
├── config.py           # All configuration constants
├── test_pipeline.py    # CLI test script
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Configuration (config.py)

| Parameter | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformer model |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `80` | Overlap between chunks |
| `TOP_K` | `5` | Chunks retrieved per query |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Free Gemini model |

---

## 🔧 Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **PDF Parsing** | PyMuPDF | Fast, accurate text extraction |
| **Embeddings** | Sentence Transformers | Free, runs locally, 384-dim vectors |
| **Vector Store** | ChromaDB | Free, local, no sign-up needed |
| **LLM** | Google Gemini 2.5 Flash | Free tier with generous limits |
| **UI** | Streamlit | Rapid prototyping, clean UI |

---

## 📈 How RAG Works (for interviews)

1. **Indexing phase**: PDFs are split into overlapping chunks. Each chunk is converted into a vector embedding (numerical representation of meaning) and stored in ChromaDB.

2. **Query phase**: The user's question is embedded using the same model. ChromaDB finds the `top-k` most semantically similar chunks using cosine similarity.

3. **Generation phase**: The retrieved chunks are injected into a prompt as context. Gemini generates an answer grounded in that context — reducing hallucinations.

---

## 🤝 Contributing

PRs welcome! Some ideas:
- Add support for `.docx`, `.txt` files
- Implement hybrid search (BM25 + semantic)
- Add re-ranking with a cross-encoder
- Stream Gemini responses token-by-token
