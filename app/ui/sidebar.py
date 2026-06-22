import os
import tempfile
import streamlit as st
from app.rag.pipeline import DocumentPipeline


def render_sidebar(pipeline: DocumentPipeline):
    with st.sidebar:

        # Brand
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-logo">🧠</div>
            <div class="sidebar-title">DocuMind AI</div>
            <div class="sidebar-version">v1.0.0 · Powered by Gemini</div>
        </div>
        """, unsafe_allow_html=True)

        # Upload section
        st.markdown(
            '<div class="sidebar-section-title">📁 Upload Documents</div>', unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Drop PDFs here",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload one or more PDF documents",
            label_visibility="collapsed"
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name
                    result = pipeline.ingest_pdf(
                        tmp_path, source_name=uploaded_file.name)
                    os.unlink(tmp_path)

                if result["success"]:
                    st.success(
                        f"✅ **{uploaded_file.name}**  \n`{result['pages']} pages · {result['chunks_stored']} chunks`")
                else:
                    st.error(f"❌ {result.get('error')}")

        # Loaded documents
        st.markdown(
            '<div class="sidebar-section-title">📚 Loaded Documents</div>', unsafe_allow_html=True)

        docs = pipeline.list_documents()
        if docs:
            for doc in docs:
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"""
                    <div class="doc-card">
                        <div class="doc-icon">📄</div>
                        <div class="doc-name" title="{doc}">{doc}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.write("")
                    if st.button("🗑", key=f"del_{doc}", help=f"Delete {doc}"):
                        deleted = pipeline.delete_document(doc)
                        st.toast(f"Deleted {doc}", icon="🗑️")
                        st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center;padding:1.5rem 0.5rem;color:#475569;font-size:0.85rem;">
                <div style="font-size:2rem;margin-bottom:0.5rem;">📭</div>
                No documents loaded yet.<br>Upload a PDF to get started.
            </div>
            """, unsafe_allow_html=True)

        # Stats
        st.markdown(
            '<div class="sidebar-section-title">📈 Database Stats</div>', unsafe_allow_html=True)
        stats = pipeline.get_collection_stats()
        st.markdown(f"""
        <div class="sidebar-stat">
            <span class="sidebar-stat-label">Total Chunks</span>
            <span class="sidebar-stat-value">{stats['total_chunks']}</span>
        </div>
        <div class="sidebar-stat" style="margin-top:0.4rem;">
            <span class="sidebar-stat-label">Documents</span>
            <span class="sidebar-stat-value">{len(docs)}</span>
        </div>
        """, unsafe_allow_html=True)

        # Footer
        st.markdown("""
        <div style="margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(99,102,241,0.2);
        text-align:center;color:#334155;font-size:0.72rem;">
            Built with ❤️ using LangChain + ChromaDB + Gemini
        </div>
        """, unsafe_allow_html=True)
