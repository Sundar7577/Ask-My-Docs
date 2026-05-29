# app.py — AskMyDocs Streamlit UI (Premium Redesign)
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
    page_icon   = "📖",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ─── Premium CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist+Mono:wght@300;400;500;600&family=Geist:wght@300;400;500;600&display=swap');

/* ── Reset & base ─────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Geist', sans-serif;
    background-color: #F7F4EF !important;
    color: #1C1917;
}

/* ── Sidebar ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #1C1917 !important;
    border-right: none !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 2rem 1.5rem !important;
}
[data-testid="stSidebar"] * {
    color: #D6D3CF !important;
}
[data-testid="stSidebar"] hr {
    border-color: #2C2927 !important;
    margin: 1.2rem 0 !important;
}

/* ── Sidebar logo ─────────────────────────────────────── */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #2C2927;
}
.sidebar-logo-icon {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, #E8C547 0%, #F0A500 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.sidebar-logo-text {
    font-family: 'Instrument Serif', serif;
    font-size: 1.35rem;
    color: #FAF9F7 !important;
    line-height: 1;
}
.sidebar-logo-sub {
    font-family: 'Geist Mono', monospace;
    font-size: 0.58rem;
    color: #57534E !important;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-top: 0.2rem;
}

/* ── Sidebar section labels ───────────────────────────── */
.sidebar-label {
    font-family: 'Geist Mono', monospace;
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: #57534E !important;
    margin-bottom: 0.6rem;
    display: block;
}

/* ── API key warning ──────────────────────────────────── */
.api-warning {
    background: #2C1810;
    border: 1px solid #7C2D12;
    border-left: 3px solid #F97316;
    border-radius: 6px;
    padding: 0.7rem 0.9rem;
    font-size: 0.78rem;
    color: #FED7AA !important;
    margin: 0.5rem 0;
    line-height: 1.5;
}
.api-warning a { color: #F97316 !important; }

/* ── Ingest success ───────────────────────────────────── */
.ingest-success {
    background: #0C1F14;
    border: 1px solid #14532D;
    border-left: 3px solid #22C55E;
    border-radius: 6px;
    padding: 0.7rem 0.9rem;
    font-size: 0.78rem;
    color: #BBF7D0 !important;
    margin: 0.5rem 0;
    line-height: 1.6;
}

/* ── Document pill ────────────────────────────────────── */
.doc-pill {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #2C2927;
    border: 1px solid #3C3937;
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    margin: 0.35rem 0;
    font-size: 0.75rem;
    color: #D6D3CF !important;
    transition: border-color 0.15s;
}
.doc-pill:hover { border-color: #E8C547; }
.doc-pill-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 140px;
    font-family: 'Geist Mono', monospace;
    font-size: 0.72rem;
    color: #A8A29E !important;
}
.doc-pill-icon { color: #E8C547 !important; margin-right: 0.4rem; }

/* ── Stack info footer ────────────────────────────────── */
.stack-info {
    background: #141211;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-top: 1rem;
}
.stack-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.25rem 0;
    font-size: 0.7rem;
    border-bottom: 1px solid #2C2927;
}
.stack-row:last-child { border-bottom: none; }
.stack-key {
    font-family: 'Geist Mono', monospace;
    color: #57534E !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 0.62rem;
}
.stack-val { color: #E8C547 !important; font-size: 0.72rem; }

/* ── Main container ───────────────────────────────────── */
.main-header {
    padding: 2.5rem 0 2rem 0;
    border-bottom: 1px solid #E5E1D8;
    margin-bottom: 2rem;
}
.main-eyebrow {
    font-family: 'Geist Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: #A09880;
    margin-bottom: 0.6rem;
}
.main-title {
    font-family: 'Instrument Serif', serif;
    font-size: 3.2rem;
    font-weight: 400;
    color: #1C1917;
    line-height: 1.05;
    margin-bottom: 0.5rem;
}
.main-title em {
    font-style: italic;
    color: #B5860D;
}
.main-subtitle {
    font-size: 0.88rem;
    color: #78716C;
    font-weight: 300;
    max-width: 520px;
    line-height: 1.6;
}

/* ── Stat chips ───────────────────────────────────────── */
.stats-row {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    margin-bottom: 2rem;
}
.stat-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #FFFFFF;
    border: 1px solid #E5E1D8;
    border-radius: 100px;
    padding: 0.3rem 0.85rem;
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem;
    color: #57534E;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stat-chip-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #22C55E;
    display: inline-block;
}
.stat-chip-dot-amber { background: #F59E0B; }
.stat-chip-dot-blue  { background: #3B82F6; }

/* ── Chat messages ────────────────────────────────────── */
.chat-wrap { max-width: 780px; margin: 0 auto; }

.msg-user {
    display: flex;
    justify-content: flex-end;
    margin: 1.2rem 0;
}
.msg-user-inner {
    background: #1C1917;
    color: #FAF9F7;
    border-radius: 18px 18px 4px 18px;
    padding: 0.9rem 1.2rem;
    max-width: 72%;
    font-size: 0.9rem;
    line-height: 1.65;
    box-shadow: 0 2px 12px rgba(0,0,0,0.12);
}

.msg-ai {
    display: flex;
    gap: 0.75rem;
    margin: 1.2rem 0;
    align-items: flex-start;
}
.msg-ai-avatar {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #E8C547, #F0A500);
    border-radius: 50%;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    margin-top: 2px;
    box-shadow: 0 2px 8px rgba(232,197,71,0.3);
}
.msg-ai-inner {
    background: #FFFFFF;
    border: 1px solid #E5E1D8;
    border-radius: 4px 18px 18px 18px;
    padding: 0.9rem 1.2rem;
    max-width: 82%;
    font-size: 0.9rem;
    line-height: 1.75;
    color: #1C1917;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.msg-ai-label {
    font-family: 'Geist Mono', monospace;
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #A09880;
    margin-bottom: 0.4rem;
}

/* ── Source chunk cards ───────────────────────────────── */
.chunk-grid { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.5rem; }
.chunk-card {
    background: #FAFAF8;
    border: 1px solid #E5E1D8;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.78rem;
    color: #57534E;
    line-height: 1.6;
    position: relative;
    overflow: hidden;
}
.chunk-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #E8C547, #F0A500);
}
.chunk-meta {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    margin-bottom: 0.4rem;
    font-family: 'Geist Mono', monospace;
    font-size: 0.65rem;
    color: #A09880;
}
.chunk-tag {
    background: #F7F4EF;
    border: 1px solid #E5E1D8;
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    font-size: 0.62rem;
}
.score-track {
    height: 3px;
    background: #E5E1D8;
    border-radius: 2px;
    margin-top: 0.6rem;
    overflow: hidden;
}
.score-fill {
    height: 100%;
    background: linear-gradient(90deg, #E8C547, #22C55E);
    border-radius: 2px;
    transition: width 0.6s ease;
}

/* ── Empty state ──────────────────────────────────────── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    max-width: 460px;
    margin: 0 auto;
}
.empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    display: block;
}
.empty-title {
    font-family: 'Instrument Serif', serif;
    font-size: 1.6rem;
    color: #1C1917;
    margin-bottom: 0.5rem;
}
.empty-desc {
    font-size: 0.85rem;
    color: #A09880;
    line-height: 1.6;
}
.empty-arrow {
    display: inline-block;
    margin-top: 1.5rem;
    font-family: 'Geist Mono', monospace;
    font-size: 0.72rem;
    color: #E8C547;
    background: #1C1917;
    border-radius: 100px;
    padding: 0.4rem 1rem;
    letter-spacing: 0.05em;
}

/* ── Streamlit overrides ──────────────────────────────── */
.stButton > button {
    background: #2C2927 !important;
    border: 1px solid #3C3937 !important;
    color: #D6D3CF !important;
    border-radius: 7px !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.78rem !important;
    padding: 0.35rem 0.75rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: #3C3937 !important;
    border-color: #E8C547 !important;
    color: #E8C547 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: #2C2927 !important;
}

.stTextInput > div > div > input {
    background: #2C2927 !important;
    border: 1px solid #3C3937 !important;
    border-radius: 7px !important;
    color: #D6D3CF !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 0.85rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #E8C547 !important;
    box-shadow: 0 0 0 2px rgba(232,197,71,0.15) !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E1D8 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'Geist', sans-serif !important;
    font-size: 0.88rem !important;
    color: #1C1917 !important;
}
[data-testid="stChatInputSubmitButton"] svg { fill: #E8C547 !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: #2C2927 !important;
    border: 1px dashed #3C3937 !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #E8C547 !important;
}

/* Multiselect */
[data-testid="stMultiSelect"] > div {
    background: #2C2927 !important;
    border-color: #3C3937 !important;
    border-radius: 7px !important;
}
.stMultiSelect span[data-baseweb="tag"] {
    background: #E8C547 !important;
    color: #1C1917 !important;
}

/* Expander */
details summary {
    font-family: 'Geist Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #A09880 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
details {
    background: #FAFAF8 !important;
    border: 1px solid #E5E1D8 !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.75rem !important;
    margin-top: 0.4rem !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #E8C547 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F7F4EF; }
::-webkit-scrollbar-thumb { background: #D6D3CF; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #A09880; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── Session state ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "active_sources" not in st.session_state:
    st.session_state.active_sources = []


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Logo ──
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">📖</div>
        <div>
            <div class="sidebar-logo-text">AskMyDocs</div>
            <div class="sidebar-logo-sub">RAG · Gemini · ChromaDB</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── API Key ──
    st.markdown('<span class="sidebar-label">Gemini API Key</span>', unsafe_allow_html=True)
    api_key = GEMINI_API_KEY or st.text_input(
        "key",
        type="password",
        placeholder="AIza••••••••••••••••••••",
        label_visibility="collapsed",
    )
    if not api_key:
        st.markdown("""<div class='api-warning'>
            ⚠ No API key detected.<br>
            Add to <code>.env</code> or paste above.<br>
            <a href='https://aistudio.google.com' target='_blank'>Get free key →</a>
        </div>""", unsafe_allow_html=True)
    else:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        st.markdown("""<div style='font-family:Geist Mono,monospace;font-size:0.68rem;
            color:#22C55E;margin:0.3rem 0 0.8rem;'>✓ API key active</div>""",
            unsafe_allow_html=True)

    st.markdown("---")

    # ── Upload ──
    st.markdown('<span class="sidebar-label">Upload Documents</span>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "upload",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded_files:
        for uf in uploaded_files:
            with st.spinner(f"Indexing {uf.name}…"):
                result = ingest_pdf(uf.read(), uf.name)
            st.markdown(f"""<div class='ingest-success'>
                ✓ <b>{result['filename']}</b><br>
                {result['pages']} pages · {result['chunks']} chunks indexed
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Indexed docs ──
    sources = list_ingested_sources()
    count   = collection_count()
    st.markdown(
        f'<span class="sidebar-label">Indexed Documents '
        f'<span style="color:#E8C547;font-size:0.7rem;">({count} chunks)</span></span>',
        unsafe_allow_html=True
    )

    if not sources:
        st.markdown("""<div style='font-size:0.78rem;color:#57534E;
            padding:0.75rem 0;font-style:italic;'>No documents yet.</div>""",
            unsafe_allow_html=True)
    else:
        selected = st.multiselect(
            "scope",
            options=sources,
            default=sources,
            label_visibility="collapsed",
        )
        st.session_state.active_sources = selected if selected else sources

        for src in sources:
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"""<div class='doc-pill'>
                    <span class='doc-pill-name'>
                        <span class='doc-pill-icon'>▪</span>{src}
                    </span>
                </div>""", unsafe_allow_html=True)
            with c2:
                if st.button("✕", key=f"del_{src}"):
                    n = delete_source(src)
                    st.toast(f"Removed {n} chunks", icon="🗑️")
                    time.sleep(0.4)
                    st.rerun()

    st.markdown("---")

    # ── Clear chat ──
    if st.button("↺  Clear conversation"):
        st.session_state.chat_history = []
        st.rerun()

    # ── Stack info ──
    st.markdown("""
    <div class="stack-info">
        <div class="stack-row">
            <span class="stack-key">Embeddings</span>
            <span class="stack-val">MiniLM-L6-v2</span>
        </div>
        <div class="stack-row">
            <span class="stack-key">LLM</span>
            <span class="stack-val">Gemini 1.5 Flash</span>
        </div>
        <div class="stack-row">
            <span class="stack-key">Vector DB</span>
            <span class="stack-val">ChromaDB</span>
        </div>
        <div class="stack-row">
            <span class="stack-key">Similarity</span>
            <span class="stack-val">Cosine · Top-5</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

# ── Header ──
st.markdown("""
<div class="main-header">
    <div class="main-eyebrow">Document Intelligence</div>
    <div class="main-title">Ask your <em>documents</em><br>anything.</div>
    <div class="main-subtitle">
        Upload PDFs, get precise answers — grounded in your content,
        with full source traceability.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Stats ──
if collection_count() > 0:
    srcs = list_ingested_sources()
    st.markdown(f"""
    <div class="stats-row">
        <span class="stat-chip"><span class="stat-chip-dot"></span>{len(srcs)} document(s) indexed</span>
        <span class="stat-chip"><span class="stat-chip-dot stat-chip-dot-amber"></span>{collection_count()} vector chunks</span>
        <span class="stat-chip"><span class="stat-chip-dot stat-chip-dot-blue"></span>Top-5 retrieval</span>
        <span class="stat-chip">Cosine similarity</span>
    </div>
    """, unsafe_allow_html=True)

# ── Chat messages ──
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-user">
            <div class="msg-user-inner">{msg['content']}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-ai">
            <div class="msg-ai-avatar">✦</div>
            <div class="msg-ai-inner">
                <div class="msg-ai-label">AskMyDocs</div>
                {msg['content']}
            </div>
        </div>""", unsafe_allow_html=True)

        if msg.get("chunks"):
            with st.expander(f"  {len(msg['chunks'])} source passages retrieved"):
                st.markdown('<div class="chunk-grid">', unsafe_allow_html=True)
                for i, chunk in enumerate(msg["chunks"], 1):
                    pct = int(chunk["score"] * 100)
                    preview = chunk['text'][:350] + ('…' if len(chunk['text']) > 350 else '')
                    st.markdown(f"""
                    <div class="chunk-card">
                        <div class="chunk-meta">
                            <span class="chunk-tag">#{i}</span>
                            <span>📄 {chunk['source']}</span>
                            <span>Page {chunk['page']}</span>
                            <span style="margin-left:auto;color:#E8C547;">{pct}% match</span>
                        </div>
                        <div style="color:#44403C;line-height:1.65;">{preview}</div>
                        <div class="score-track">
                            <div class="score-fill" style="width:{pct}%;"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Empty state ──
if collection_count() == 0:
    st.markdown("""
    <div class="empty-state">
        <span class="empty-icon">📂</span>
        <div class="empty-title">No documents yet</div>
        <div class="empty-desc">
            Upload a PDF in the sidebar. It'll be chunked, embedded locally
            with Sentence Transformers, and stored in ChromaDB — ready to query instantly.
        </div>
        <div class="empty-arrow">← Upload a PDF to begin</div>
    </div>
    """, unsafe_allow_html=True)

# ── Chat input ──
query = st.chat_input("Ask anything about your documents…")

if query:
    if not (GEMINI_API_KEY or api_key):
        st.error("Please provide a Gemini API key in the sidebar.")
    elif collection_count() == 0:
        st.warning("Please upload at least one PDF first.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": query})

        with st.spinner("Retrieving · Generating…"):
            result = generate_answer(
                query         = query,
                source_filter = st.session_state.active_sources or None,
                chat_history  = st.session_state.chat_history,
            )

        st.session_state.chat_history.append({
            "role":    "assistant",
            "content": result["answer"],
            "chunks":  result["chunks"],
        })

        st.rerun()