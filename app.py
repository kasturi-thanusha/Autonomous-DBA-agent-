"""
app.py
------
Premium Streamlit Dashboard for the Autonomous DBA Agent.
Provides visibility into the agent's work.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from core.config import settings
from core.db.postgres import db_manager
from core.db.queries import fetch_slow_queries
from core.store.repository import repo
from core.ai.analyzer import analyzer
from core.logging_config import logger

# Page configuration
st.set_page_config(
    page_title="Slow Query AI Agent | Autonomous DBA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 20px; border-radius: 10px; border: 1px solid #3e4150; }
    .stAlert { border-radius: 10px; }
    .stButton > button { width: 100%; border-radius: 5px; }
    .sidebar .sidebar-content { background-image: linear-gradient(180deg, #1e2130, #0e1117); }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🤖 Autonomous DBA Agent")
    st.subheader("PostgreSQL Performance Optimization dashboard")
    
    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Connection Status")
        is_online = db_manager.test_connection()
        if is_online:
            st.success("🟢 PostgreSQL Online")
        else:
            st.error("🔴 PostgreSQL Offline")
            
        st.divider()
        st.info(f"Monitoring Threshold: {settings.slow_query_threshold_ms}ms")
        st.info(f"Capture Interval: {settings.capture_interval_minutes}m")
        
        if st.button("Manual Refresh"):
            st.rerun()

    # ── KPI Row ─────────────────────────────────────────────────────────────
    recs = repo.get_all()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Identified Queries", len(recs))
    with col2:
        analyzed_count = sum(1 for r in recs if r.analysis)
        st.metric("AI Analyzed", analyzed_count)
    with col3:
        top_impact = max([r.total_impact_pct for r in recs]) if recs else 0
        st.metric("Max Impact", f"{round(top_impact, 1)}%")
    with col4:
        st.metric("MCP Status", "Waiting for client...")

    # ── Main Content ─────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🔥 Top Slow Queries", "🧠 AI Recommendations", "📊 Health & Logs"])

    with tab1:
        st.write("### Live Performance Scan")
        live_queries = fetch_slow_queries(limit=10)
        if live_queries:
            df = pd.DataFrame(live_queries)
            # Visualize impact
            fig = px.bar(df, x='queryid', y='mean_exec_time', color='total_impact_pct',
                         title="Query Mean Execution Time (ms)", 
                         labels={'mean_exec_time': 'Time (ms)', 'queryid': 'Query ID'},
                         template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df, use_container_width=True)
            
            # Action selection
            st.write("#### Trigger AI Analysis")
            selected_qid = st.selectbox("Select Query to Optimize", df['queryid'].tolist())
            if st.button("Deep Analyze with Groq"):
                selected_q = next(q for q in live_queries if q['queryid'] == selected_qid)
                repo.upsert_query_meta(selected_q) # Ensure in DB
                
                with st.spinner(f"AI is thinking about {selected_qid}..."):
                    result = analyzer.analyze(selected_q)
                    repo.save_ai_analysis(selected_qid, result)
                    st.success("Analysis complete! View it in the Recommendations tab.")
        else:
            st.info("No slow queries found matching the threshold.")

    with tab2:
        st.write("### Optimization Knowledge Base")
        if recs:
            for r in recs:
                if r.analysis:
                    with st.expander(f"📌 Query: {r.queryid} | Impact: {round(r.total_impact_pct, 1)}%"):
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            st.code(r.original_query, language='sql')
                            st.write("**AI Analysis:**")
                            st.markdown(r.analysis)
                        with c2:
                            st.write("**Confidence Score**")
                            st.progress(r.confidence_score or 0.0)
                            
                            st.write("**Recommended Index**")
                            st.code(r.index_suggestion, language='sql')
                            
                        st.divider()
                        st.write("**Optimized Query**")
                        st.code(r.rewritten_query, language='sql')
                else:
                    st.write(f"⏳ {r.queryid} is pending analysis.")
        else:
            st.info("No analyzed recommendations yet.")

    with tab3:
        st.write("### System Logs (Recent Activity)")
        try:
            with open(settings.log_file, "r") as f:
                logs = f.readlines()[-20:]
                st.code("".join(logs))
        except:
            st.warning("Log file not found yet.")

if __name__ == "__main__":
    main()
