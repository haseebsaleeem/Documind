import streamlit as st
import pandas as pd
from app.analytics.data_analyzer import DataAnalyzer


def render_analytics():
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <h2 style="margin:0;font-size:1.3rem;font-weight:700;color:#f1f5f9;">
            📊 Data Analytics Engine
        </h2>
        <p style="margin:0.2rem 0 0 0;font-size:0.85rem;color:#64748b;">
            Upload CSV or Excel files for automated analysis, visualizations, and AI-powered insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx", "xls"],
        key="analytics_upload",
        label_visibility="collapsed"
    )

    if uploaded is None:
        st.markdown("""
        <div style="text-align:center;padding:4rem 1rem;color:#334155;">
            <div style="font-size:3.5rem;margin-bottom:1rem;">📊</div>
            <div style="font-size:1.1rem;font-weight:600;color:#64748b;margin-bottom:0.5rem;">
                Drop a CSV or Excel file to begin
            </div>
            <div style="font-size:0.85rem;color:#475569;">
                Get instant statistics, charts, anomaly detection, and AI insights
            </div>
            <div style="display:flex;gap:0.5rem;justify-content:center;margin-top:1.5rem;flex-wrap:wrap;">
                <span class="source-chip">📈 Auto Charts</span>
                <span class="source-chip">⚠️ Anomaly Detection</span>
                <span class="source-chip">🤖 AI Insights</span>
                <span class="source-chip">📋 Statistics</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    analyzer = DataAnalyzer()
    with st.spinner("Analyzing your data..."):
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
        analyzer.load_dataframe(df, uploaded.name)
        summary = analyzer.get_summary()

    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{summary['shape']['rows']:,}</div>
            <div class="stat-label">Total Rows</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{summary['shape']['columns']}</div>
            <div class="stat-label">Columns</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(summary['numeric_columns'])}</div>
            <div class="stat-label">Numeric Cols</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        missing_total = sum(
            v for v in summary['missing_values'].values() if v > 0)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="background:linear-gradient(135deg,#f59e0b,#ef4444);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">{missing_total}</div>
            <div class="stat-label">Missing Values</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Data Preview",
        "📈 Visualizations",
        "⚠️ Anomalies",
        "🤖 AI Insights"
    ])

    with tab1:
        st.dataframe(df.head(50), use_container_width=True)
        if "statistics" in summary:
            st.markdown("**Descriptive Statistics**")
            st.dataframe(pd.DataFrame(summary["statistics"]).round(
                4), use_container_width=True)

    with tab2:
        with st.spinner("Generating charts..."):
            charts = analyzer.generate_charts()
        if charts:
            for chart in charts:
                st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Not enough numeric data to generate charts.")

    with tab3:
        anomalies = analyzer.detect_anomalies()
        if anomalies:
            st.markdown(f"""
            <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);
            border-radius:12px;padding:1rem 1.2rem;margin-bottom:1rem;">
                <span style="color:#fbbf24;font-weight:600;">⚠️ {len(anomalies)} column(s) with anomalies detected</span>
            </div>
            """, unsafe_allow_html=True)
            for a in anomalies:
                with st.expander(f"📊 {a['column']} — {a['outlier_count']} outliers ({a['outlier_percent']}%)"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Outliers", a["outlier_count"])
                    c2.metric("Lower Bound", round(a["lower_bound"], 2))
                    c3.metric("Upper Bound", round(a["upper_bound"], 2))
                    st.caption(
                        f"Sample outlier values: {a['sample_outliers']}")
        else:
            st.markdown("""
            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
            border-radius:12px;padding:1rem 1.2rem;">
                <span style="color:#34d399;font-weight:600;">✅ No significant anomalies detected</span>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        with st.spinner("Generating AI insights..."):
            insights = analyzer.ai_insights()
        st.markdown(
            f'<div class="fade-in">{insights}</div>', unsafe_allow_html=True)
