import streamlit as st
from app.config import config
from app.styles import get_custom_css
from app.rag.pipeline import DocumentPipeline
from app.rag.retriever import RAGRetriever
from app.agent import DocuMindAgent
from app.ui.sidebar import render_sidebar
from app.ui.chat_ui import render_chat
from app.ui.analytics_ui import render_analytics
from app.evaluation.evaluator import RAGEvaluator


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Inject CSS ───────────────────────────────────────────────────────────────
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ── Validate API Key ─────────────────────────────────────────────────────────
if not config.GEMINI_API_KEY:
    st.markdown("""
    <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
    border-radius:14px;padding:1.5rem 2rem;margin:2rem 0;">
        <h3 style="color:#f87171;margin:0 0 0.5rem 0;">⚠️ API Key Missing</h3>
        <p style="color:#94a3b8;margin:0;">Add your <code>GEMINI_API_KEY</code> to the <code>.env</code> file and restart.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Shared ChromaDB collection ───────────────────────────────────────────────
@st.cache_resource
def load_shared_collection():
    import chromadb
    client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    collection = client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    return collection


@st.cache_resource
def load_pipeline(_collection):
    return DocumentPipeline(collection=_collection)


@st.cache_resource
def load_retriever(_collection):
    return RAGRetriever(collection=_collection)


@st.cache_resource
def load_agent(_collection):
    return DocuMindAgent(collection=_collection)


@st.cache_resource
def load_evaluator(_collection):
    return RAGEvaluator(collection=_collection)


collection = load_shared_collection()
pipeline = load_pipeline(collection)
retriever = load_retriever(collection)
agent = load_agent(collection)
evaluator = load_evaluator(collection)


# ── Evaluation renderer ──────────────────────────────────────────────────────
def render_evaluation(evaluator, pipeline):
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="margin:0;font-size:1.3rem;font-weight:700;color:#f1f5f9;">
            🧪 RAG Evaluation Suite
        </h2>
        <p style="margin:0.2rem 0 0 0;font-size:0.85rem;color:#64748b;">
            Benchmark retrieval accuracy, response quality, and latency.
        </p>
    </div>
    """, unsafe_allow_html=True)

    default_tests = [
        {"query": "What is the main purpose of this document?", "expected": ""},
        {"query": "What are the key findings or conclusions?",   "expected": ""},
        {"query": "Are there any risks or limitations mentioned?", "expected": ""},
    ]

    test_queries = []
    for i, tc in enumerate(default_tests):
        col1, col2 = st.columns([2, 2])
        with col1:
            q = st.text_input(f"Query {i+1}", value=tc["query"], key=f"q_{i}")
        with col2:
            e = st.text_input(f"Expected answer (optional)",
                              value=tc["expected"], key=f"e_{i}")
        test_queries.append({"query": q, "expected": e})

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("▶️ Run Evaluation", type="primary"):
        if pipeline.get_collection_stats()["total_chunks"] == 0:
            st.warning("⚠️ No documents loaded. Upload PDFs first.")
        else:
            with st.spinner("Running evaluation suite..."):
                report = evaluator.run_benchmark(
                    [t for t in test_queries if t["query"]]
                )

            m = report["metrics"]

            # Metric cards
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{m['avg_latency']}s</div>
                    <div class="stat-label">Avg Latency</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{m['avg_similarity']}</div>
                    <div class="stat-label">Avg Similarity</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{m['avg_quality_score']}/5</div>
                    <div class="stat-label">Avg Quality</div>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{m['high_confidence_rate']*100:.0f}%</div>
                    <div class="stat-label">High Confidence</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Individual results
            for r in report["individual_results"]:
                with st.expander(f"📋 Q: {r['query'][:80]}"):
                    st.markdown(f"""
                    <div style="background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.15);
                    border-radius:10px;padding:1rem;margin-bottom:1rem;color:#94a3b8;
                    font-size:0.88rem;line-height:1.7;">
                        {r['answer'][:600]}
                    </div>
                    """, unsafe_allow_html=True)

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("⚡ Latency",    f"{r['latency_seconds']}s")
                    col2.metric("🎯 Similarity", r['avg_similarity'])
                    col3.metric("🔮 Confidence", r['confidence'])
                    col4.metric(
                        "⭐ Quality",    f"{r.get('quality_score', 0)}/5")

                    if r.get("feedback"):
                        st.markdown(f"""
                        <div style="background:rgba(6,182,212,0.05);border:1px solid rgba(6,182,212,0.15);
                        border-radius:8px;padding:0.6rem 0.8rem;margin-top:0.5rem;
                        color:#22d3ee;font-size:0.82rem;">
                            💬 {r['feedback']}
                        </div>
                        """, unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="documind-header fade-in">
    <div class="header-content">
        <div class="header-icon">🧠</div>
        <div>
            <h1 class="header-title">DocuMind AI</h1>
            <p class="header-subtitle">AI-Powered Document Intelligence & Decision Assistant</p>
            <div class="header-badges">
                <span class="badge">RAG Pipeline</span>
                <span class="badge badge-cyan">Gemini 2.5</span>
                <span class="badge badge-amber">AI Agent</span>
                <span class="badge badge-green">ChromaDB</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────
render_sidebar(pipeline)


# ── Main Tabs ────────────────────────────────────────────────────────────────
tab_chat, tab_analytics, tab_eval = st.tabs([
    "💬  Chat with Documents",
    "📊  Data Analytics",
    "🧪  Evaluation"
])

with tab_chat:
    render_chat(retriever, agent)

with tab_analytics:
    render_analytics()

with tab_eval:
    render_evaluation(evaluator, pipeline)
