import streamlit as st
from app.rag.retriever import RAGRetriever
from app.agent import DocuMindAgent


def render_chat(retriever: RAGRetriever, agent: DocuMindAgent):

    # Top bar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div style="margin-bottom:1rem;">
            <h2 style="margin:0;font-size:1.3rem;font-weight:700;color:#f1f5f9;">
                💬 Chat with your Documents
            </h2>
            <p style="margin:0.2rem 0 0 0;font-size:0.85rem;color:#64748b;">
                Ask anything — get cited, intelligent answers from your uploaded documents.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        mode = st.selectbox(
            "Mode",
            ["🔍 RAG Search", "🤖 AI Agent"],
            label_visibility="collapsed"
        )

    # Mode info banner
    if "Agent" in mode:
        st.markdown("""
        <div class="reasoning-box" style="margin-bottom:1rem;">
            <div class="reasoning-title">🤖 AI Agent Mode Active</div>
            <div style="color:#94a3b8;font-size:0.83rem;">
                The agent will plan, reason, and execute multiple steps to answer complex queries.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat history init
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Welcome message when empty
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#334155;">
            <div style="font-size:3.5rem;margin-bottom:1rem;">🧠</div>
            <div style="font-size:1.1rem;font-weight:600;color:#64748b;margin-bottom:0.5rem;">
                Ready to answer your questions
            </div>
            <div style="font-size:0.85rem;color:#475569;">
                Upload a PDF from the sidebar, then ask anything about it.
            </div>
            <div style="display:flex;gap:0.5rem;justify-content:center;margin-top:1.5rem;flex-wrap:wrap;">
                <span class="source-chip">💡 What is this document about?</span>
                <span class="source-chip">📋 Summarize the key points</span>
                <span class="source-chip">⚠️ Identify any risks</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources") and msg["role"] == "assistant":
                _render_sources_inline(
                    msg.get("sources", []),
                    msg.get("confidence", "low"),
                    msg.get("contexts", [])
                )

    # Chat input
    if prompt := st.chat_input("Ask anything about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]
                ]

                if "Agent" in mode:
                    result = agent.run(prompt, history)
                    if result.get("agent_reasoning"):
                        st.markdown(f"""
                        <div class="reasoning-box fade-in">
                            <div class="reasoning-title">🧠 Agent Reasoning</div>
                            <div style="color:#94a3b8;font-size:0.83rem;">
                                <b style="color:#fbbf24;">Intent:</b> {result['plan'].get('intent', '')}<br>
                                <b style="color:#fbbf24;">Plan:</b> {result['plan'].get('reasoning', '')}<br>
                                <b style="color:#fbbf24;">Actions:</b> {' → '.join(result['plan'].get('actions', []))}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    result = retriever.answer(prompt, history)

            answer = result.get("answer", "No answer generated.")
            sources = result.get("sources", [])
            contexts = result.get("contexts", [])
            confidence = result.get("confidence", "unknown")

            st.markdown(
                f'<div class="fade-in">{answer}</div>', unsafe_allow_html=True)

            if sources:
                _render_sources_inline(sources, confidence, contexts)

        st.session_state.messages.append({
            "role":       "assistant",
            "content":    answer,
            "sources":    sources,
            "contexts":   contexts,
            "confidence": confidence
        })

    # Clear button
    if st.session_state.messages:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([4, 1, 4])
        with col2:
            if st.button("🗑️ Clear", help="Clear chat history"):
                st.session_state.messages = []
                st.rerun()


def _render_sources_inline(sources, confidence, contexts):
    conf_map = {
        "high":   ("conf-high",   "● High Confidence"),
        "medium": ("conf-medium", "◐ Medium Confidence"),
        "low":    ("conf-low",    "○ Low Confidence"),
    }
    css_class, label = conf_map.get(confidence, ("conf-low", "○ Unknown"))
    chips = "".join(
        [f'<span class="source-chip">📄 {s}</span>' for s in sources])

    st.markdown(f"""
    <div style="margin-top:0.8rem;padding-top:0.8rem;
    border-top:1px solid rgba(99,102,241,0.15);">
        <div style="display:flex;align-items:center;gap:0.8rem;
        flex-wrap:wrap;margin-bottom:0.5rem;">
            <span class="{css_class}">{label}</span>
            {chips}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if contexts:
        with st.expander("🔍 View Retrieved Chunks"):
            for ctx in contexts[:3]:
                st.markdown(f"""
                <div style="background:rgba(99,102,241,0.05);
                border:1px solid rgba(99,102,241,0.15);
                border-radius:10px;padding:0.8rem 1rem;margin-bottom:0.6rem;">
                    <div style="display:flex;align-items:center;
                    justify-content:space-between;margin-bottom:0.4rem;">
                        <span style="font-size:0.78rem;font-weight:600;
                        color:#818cf8;">📄 {ctx['source']}</span>
                        <span style="font-size:0.72rem;color:#475569;">
                        similarity: {ctx['similarity']}</span>
                    </div>
                    <div style="font-size:0.83rem;color:#94a3b8;
                    line-height:1.6;">{ctx['text'][:350]}...</div>
                </div>
                """, unsafe_allow_html=True)
