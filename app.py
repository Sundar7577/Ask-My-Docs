# app.py — AskMyDocs Streamlit UI
# Run with: streamlit run app.py

import streamlit as st
import os
import time
from ingest import ingest_pdf, list_ingested_sources, delete_source, collection_count
from generator import generate_answer
from config import GEMINI_API_KEY

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title  = "AskMyDocs",
    page_icon   = "📚",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0d0f14;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #111318 !important;
    border-right: 1px solid #1e2330;
}

/* Main title */
.main-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 60%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
}

.subtitle {
    color: #64748b;
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* Chat messages */
.chat-bubble-user {
    background: #1e2330;
    border: 1px solid #2a3244;
    border-radius: 12px 12px 4px 12px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    margin-left: 15%;
    color: #e2e8f0;
    font-size: 0.9rem;
    line-height: 1.6;
}

.chat-bubble-ai {
    background: #0f1620;
    border: 1px solid #1d3461;
    border-left: 3px solid #38bdf8;
    border-radius: 4px 12px 12px 12px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    margin-right: 15%;
    color: #cbd5e1;
    font-size: 0.9rem;
    line-height: 1.7;
}

.role-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.4rem;
    font-weight: 600;
}
.role-label-user { color: #818cf8; }
.role-label-ai   { color: #38bdf8; }

/* Source chunk cards */
.chunk-card {
    background: #111827;
    border: 1px solid #1e2d3d;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.4rem 0;
    font-size: 0.78rem;
    color: #94a3b8;
    line-height: 1.6;
}

.chunk-meta {
    font-size: 0.7rem;
    color: #475569;
    margin-bottom: 0.4rem;
    font-family: 'DM Mono', monospace;
}

.score-bar-container {
    background: #1e2330;
    border-radius: 4px;
    height: 4px;
    margin-top: 0.5rem;
}

.score-bar {
    height: 4px;
    border-radius: 4px;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
}

/* Stat chips */
.stat-chip {
    display: inline-block;
    background: #1a2236;
    border: 1px solid #243050;
    border-radius: 20px;
    padding: 0.25rem 0.8rem;
    font-size: 0.75rem;
    color: #64748b;
    margin: 0.2rem;
}

/* File tag */
.file-tag {
    background: #0f2339;
    border: 1px solid #1e4067;
    border-radius: 6px;
    padding: 0.3rem 0.7rem;
    font-size: 0.78rem;
    color: #38bdf8;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0.3rem 0;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1d3461, #1e2d4d) !important;
    border: 1px solid #2a4a7f !important;
    color: #93c5fd !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1e4080, #2563eb) !important;
    color: #fff !important;
    border-color: #3b82f6 !important;
}

/* Input box */
.stTextInput > div > div > input,
.stChatInput > div > div > input,
textarea {
    background: #111827 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.88rem !important;
}

/* Warning / Info */
.warning-box {
    background: #1a1500;
    border: 1px solid #3d3000;
    border-left: 3px solid #f59e0b;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    font-size: 0.82rem;
    color: #fcd34d;
    margin: 0.5rem 0;
}

.info-box {
    background: #071628;
    border: 1px solid #1d3d6b;
    border-left: 3px solid #38bdf8;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    font-size: 0.82rem;
    color: #7dd3fc;
    margin: 0.5rem 0;
}

/* Divider */
hr { border-color: #1e2330 !important; }

/* Expander */
.streamlit-expanderHeader {
    background: #111318 !important;
    color: #64748b !important;
    font-size: 0.8rem !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #1e2d3d; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ─── Session state init ────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []          # [{role, content, chunks?}]
if "active_sources" not in st.session_state:
    st.session_state.active_sources = []        # files to scope retrieval to


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 0.5rem 0 1.5rem 0;'>
        <div style='font-family: Syne, sans-serif; font-size: 1.4rem; font-weight: 800;
                    background: linear-gradient(135deg, #38bdf8, #818cf8);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            📚 AskMyDocs
        </div>
        <div style='color: #334155; font-size: 0.7rem; text-transform: uppercase;
                    letter-spacing: 0.1em; margin-top: 0.2rem;'>RAG · Gemini · ChromaDB</div>
    </div>
    """, unsafe_allow_html=True)

    # ── API Key check ──
    api_key = GEMINI_API_KEY or st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Get a free key at aistudio.google.com",
    )
    if not api_key:
        st.markdown("""<div class='warning-box'>
            ⚠️ Add your Gemini API key to <code>.env</code> or paste it above.<br>
            <a href='https://aistudio.google.com' target='_blank' style='color:#f59e0b;'>
            Get free key →</a></div>""", unsafe_allow_html=True)
    else:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

    st.markdown("---")

    # ── PDF Upload ──
    st.markdown("<div style='font-size:0.75rem;color:#475569;text-transform:uppercase;"
                "letter-spacing:0.1em;margin-bottom:0.6rem;'>Upload Documents</div>",
                unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop PDFs here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        for uf in uploaded_files:
            with st.spinner(f"Ingesting {uf.name}…"):
                result = ingest_pdf(uf.read(), uf.name)
            st.markdown(f"""<div class='info-box'>
                ✅ <b>{result['filename']}</b><br>
                {result['pages']} pages · {result['chunks']} chunks indexed
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Indexed documents ──
    sources = list_ingested_sources()
    count   = collection_count()

    st.markdown(f"<div style='font-size:0.75rem;color:#475569;text-transform:uppercase;"
                f"letter-spacing:0.1em;margin-bottom:0.6rem;'>Indexed Documents "
                f"<span style='color:#1e4067;'>({count} chunks)</span></div>",
                unsafe_allow_html=True)

    if not sources:
        st.markdown("<div style='color:#334155;font-size:0.8rem;padding:0.5rem 0;'>"
                    "No documents yet. Upload a PDF above.</div>", unsafe_allow_html=True)
    else:
        # Scope filter
        selected = st.multiselect(
            "Scope retrieval to:",
            options=sources,
            default=sources,
            label_visibility="collapsed",
        )
        st.session_state.active_sources = selected if selected else sources

        # Delete buttons
        for src in sources:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"<div style='font-size:0.78rem;color:#38bdf8;padding:0.3rem 0;"
                            f"overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
                            f"max-width:160px;' title='{src}'>📄 {src}</div>",
                            unsafe_allow_html=True)
            with col2:
                if st.button("✕", key=f"del_{src}"):
                    n = delete_source(src)
                    st.success(f"Deleted {n} chunks")
                    time.sleep(0.5)
                    st.rerun()

    st.markdown("---")

    # ── Controls ──
    if st.button("🗑️ Clear chat history"):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("""
    <div style='margin-top:1.5rem;padding-top:1rem;border-top:1px solid #1e2330;
                font-size:0.7rem;color:#334155;line-height:1.8;'>
        <div>🔗 <b style='color:#475569'>Embeddings:</b> all-MiniLM-L6-v2</div>
        <div>🤖 <b style='color:#475569'>LLM:</b> gemini-1.5-flash</div>
        <div>🗄️ <b style='color:#475569'>VectorDB:</b> ChromaDB (local)</div>
        <div>📐 <b style='color:#475569'>Strategy:</b> Cosine similarity</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Main area ────────────────────────────────────────────────────────────────
st.markdown("<div class='main-title'>AskMyDocs</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Retrieval-Augmented Generation · Chat with your PDFs</div>",
            unsafe_allow_html=True)

# Stats row
if collection_count() > 0:
    sources = list_ingested_sources()
    st.markdown(
        f"<span class='stat-chip'>📄 {len(sources)} document(s)</span>"
        f"<span class='stat-chip'>🧩 {collection_count()} chunks</span>"
        f"<span class='stat-chip'>🎯 Top-5 retrieval</span>"
        f"<span class='stat-chip'>🌡️ Cosine similarity</span>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

# ── Chat history display ──
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class='chat-bubble-user'>
            <div class='role-label role-label-user'>You</div>
            {msg['content']}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='chat-bubble-ai'>
            <div class='role-label role-label-ai'>Assistant</div>
            {msg['content']}
        </div>""", unsafe_allow_html=True)

        # Show source chunks in expander
        if msg.get("chunks"):
            with st.expander(f"📎 {len(msg['chunks'])} source chunks used"):
                for i, chunk in enumerate(msg["chunks"], 1):
                    pct = int(chunk["score"] * 100)
                    st.markdown(f"""
                    <div class='chunk-card'>
                        <div class='chunk-meta'>
                            [{i}] {chunk['source']} · Page {chunk['page']} · Relevance {pct}%
                        </div>
                        {chunk['text'][:400]}{'…' if len(chunk['text']) > 400 else ''}
                        <div class='score-bar-container'>
                            <div class='score-bar' style='width:{pct}%;'></div>
                        </div>
                    </div>""", unsafe_allow_html=True)

# ── Chat input ──
st.markdown("<br>", unsafe_allow_html=True)

if collection_count() == 0:
    st.markdown("""<div class='info-box'>
        👈 Upload a PDF in the sidebar to get started. The system will chunk and embed it locally
        using Sentence Transformers, then you can ask questions answered by Gemini.
    </div>""", unsafe_allow_html=True)

query = st.chat_input("Ask anything about your documents…")

if query:
    if not (GEMINI_API_KEY or api_key):
        st.error("Please provide a Gemini API key in the sidebar.")
    elif collection_count() == 0:
        st.warning("Please upload at least one PDF first.")
    else:
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": query})

        with st.spinner("Retrieving relevant chunks and generating answer…"):
            result = generate_answer(
                query         = query,
                source_filter = st.session_state.active_sources or None,
                chat_history  = st.session_state.chat_history,
            )

        # Append AI response with chunks
        st.session_state.chat_history.append({
            "role":    "assistant",
            "content": result["answer"],
            "chunks":  result["chunks"],
        })

        st.rerun()
