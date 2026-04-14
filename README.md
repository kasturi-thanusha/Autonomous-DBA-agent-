# 🤖 Autonomous AI DBA Agent

Building a Production-Grade Autonomous PostgreSQL Optimization System

## 📖 What is this project about?
The **Autonomous AI DBA Agent** operates exactly like an invisible Database Administrator inside your systems. It continuously monitors live PostgreSQL databases to capture underperforming queries, analyzes their low-level execution structures (`EXPLAIN ANALYZE`), communicates directly with large action models (Groq LLaMA-based models) to infer optimizations, and constructs rigorous theoretical indexing strategies.

Crucially, it utilizes a **Safe Execution Layer**. Instead of aggressively patching production tables, it tests its AI-generated theories locally by dry-running database indices within locked transaction blocks (`BEGIN...ROLLBACK`). Because of this, it validates performance improvements autonomously, guaranteeing metrics like "percentage-based workload reductions" before a human engineer ever touches a button.

Everything operates across three paradigms: an invisible background daemon (`scheduler/monitor.py`), an interactive frontend (`app.py` Streamlit dashboard), and an API protocol designed natively for Claude AI Desktop integration (`mcp_server/server.py`).

---

## 🏗️ System Workflow & Architecture

The system seamlessly combines Model Context Protocol (MCP), real-time database monitoring, advanced AI integration (Groq), and a safe execution layer to validate AI theories securely.

### **1. 🔴 Real-Time Threat Trigger (The Capture Layer)**
A silent background Python worker (`scheduler/monitor.py`) polls PostgreSQL's `pg_stat_statements` every few minutes. If a query suddenly averages longer than 500ms, the system bypasses its batch cycle and dynamically isolates the query for an immediate AI health review.

### **2. 🧠 EXPLAIN ANALYZE Extraction (The Intelligence Layer)**
Once flagged, the system actively queries the database for the exact unoptimized query's internal tree structure using `EXPLAIN (ANALYZE, BUFFERS)`. This low-level metric blueprint is piped to the **Groq AI Engine** (`core/ai/analyzer.py`), stripping away hallucination by providing the AI with accurate, objective execution bottlenecks. It returns a JSON structure containing root cause analysis, an optimized query rewrite, and index suggestions.

### **3. 🛡️ Safe Execution Layer (The Validation Layer)**
The AI proposes a complete schema restructuring. The agent intercepts this inside `core/db/queries.py` and runs a **Safe Validation**:
  - `BEGIN;` (start an isolated transaction block)
  - `CREATE INDEX...` (test the AI's idea)
  - Extract the new reduced Cost Metric.
  - Automatically calculate the `🚀 Performance Improvement %`.
  - `ROLLBACK;` (completely revert the sandbox changes).

This produces **verifiable, data-proven** metrics before recommending the solution permanently.

### **4. 📊 Dashboard Visualization (The UI Layer)**
All identified bottlenecks and their calculated percentage improvements are persisted cleanly inside a local SQLite knowledge-base (`data/recommendations.db`). This powers the **Premium Streamlit Dashboard** (`app.py`), which maps high-impact performance disruptions to dynamic bar charts and explicit AI analyses dynamically on your browser.

### **5. 🔌 Model Context Protocol (The Integration Layer)**
A distinct `FastMCP` architecture allows external clients, explicitly the standalone **Claude Desktop App**, to interact securely with the agent. By hooking Claude Desktop into this Python interface (`mcp_server/server.py`), external users can remotely command the agent via chat to: 
- `list_slow_queries()` 
- `analyze_query_performance(query_id)`
- `show_db_health()`
- `read_agent_logs(lines)`

---

## 🛠️ Technology Stack
- **Backend Infrastructure:** Python 3.12, APScheduler (Daemons)
- **Database Architecture:** PostgreSQL (`psycopg2`, `pg_stat_statements`)
- **LLM Agent Inference:** Groq API SDK (High-Speed LLaMA Models)
- **Local Analytics Storage:** SQLite + SQLAlchemy
- **Interactive UI Dashboard:** Streamlit + Plotly (Dark Mode/Premium Layouts)
- **Client Protocol Exposer:** Model Context Protocol Server (FastMCP)

---

## 🚀 Setup Instructions

### 1. Environment Setup
To set up this workspace locally, you need Python 3.12 (or higher) and a running instance of PostgreSQL.

**Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows WSL/Linux/macOS
# On Windows PowerShell: .\venv\Scripts\Activate.ps1
```

**Install the dependencies:**
```bash
pip install -r requirements.txt
```

### 2. Configuration (`.env`)
You must configure your `.env` file in the root project directory before starting. Copy `.env.example` to `.env` and fill in:

```env
# PostgreSQL Database Credentials
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password

# Groq AI Keys
GROQ_API_KEY=gsk_your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Database Preparation
Ensure your PostgreSQL database has the `pg_stat_statements` extension enabled. This allows the AI agent to capture slow queries natively:
1. Connect to your database.
2. Run: `CREATE EXTENSION IF NOT EXISTS pg_stat_statements;`

---

## 🏃 Execution Steps

The architecture is multi-faceted. You can run individual components based on your current need. Ensure your virtual environment is active before running.

### 1. Run the Dashboard (Streamlit)
To visualize identified optimizations, AI metrics, and trigger tasks manually:
```bash
streamlit run app.py
```
This boots up a premium Web UI dynamically hosted at `http://localhost:8501`.

### 2. Start the Real-Time Background Monitor
To enable the agent to act purely autonomously in the background (capturing spikes and generating Groq insights without human interaction):
```bash
python -m scheduler.monitor
```
*Note: This runs infinitely in the terminal daemon until you press `Ctrl+C`.*

### 3. Expose the Agent Tools to Claude (MCP Server)
If you want to plug the optimization tools directly into Claude Desktop using the Model Context Protocol:
Add the following to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "Postgres-Optimizer": {
      "command": "python",
      "args": ["/absolute/path/to/slow query ai agent/mcp_server/server.py"]
    }
  }
}
```
Restart Claude Desktop, and you can now ask Claude questions like *"What queries are currently running slow in my database?"* and it will invoke the local Python server internally.
