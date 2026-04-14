# Autonomous AI DBA Agent - System Explanation

## System Architecture

The Autonomous DBA Agent is a production-grade system designed to automatically identify, analyze, and optimize slow queries within an active PostgreSQL database. 

It seamlessly combines:
1. **Model Context Protocol (MCP)** for exposing agentic database tools directly to Claude Desktop.
2. **Real-Time Database Monitoring** via an APScheduler daemon to catch live query latency spikes.
3. **Advanced AI Integration (Groq)** to interpret `EXPLAIN ANALYZE` trees.
4. **Safe Execution Layer** to validate AI theories securely.

## Core Components
- `core/db/queries.py`: Connects directly to `pg_stat_statements` and retrieves high-impact execution queries. It also features a "Safe Validation" mechanism where the AI's suggested indices are temporarily dry-run in a transaction (`BEGIN -> test -> ROLLBACK`) to measure absolute performance improvement percentages.
- `core/ai/analyzer.py`: When a threshold spike is detected (e.g., >500ms), the query text and its raw execution plan (`EXPLAIN (ANALYZE, BUFFERS)`) are piped dynamically to an LLM via Groq. The AI returns a JSON structure containing root cause analysis, an optimized query rewrite, and index suggestions.
- `scheduler/monitor.py`: A native background daemon that acts as a real-time hardware trigger. It polls the database every few minutes and immediately bridges the highest-impact bottlenecks to the AI logic.
- `app.py`: A premium Streamlit dashboard constructed to visualize the local SQLite knowledge-base (`data/recommendations.db`). It natively plots improvement percentages, severity charts, and agent activities.
- `mcp_server/server.py`: The `FastMCP` gateway mapping internal agent tools (`analyze_query_performance`, `list_slow_queries`) directly to an external orchestrator (like Claude Desktop).
