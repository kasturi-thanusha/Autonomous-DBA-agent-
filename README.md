# 🤖 Autonomous AI DBA Agent
## Building a Production-Grade Autonomous PostgreSQL Optimization System

---

## 📖 What is this project about?

The **Autonomous AI DBA Agent** operates exactly like an invisible Database Administrator inside your systems. It continuously monitors live PostgreSQL databases to capture underperforming queries, analyzes their low-level execution structures (EXPLAIN ANALYZE), communicates directly with large action models (Groq LLaMA-based models) to infer optimizations, and constructs rigorous theoretical indexing strategies.

Crucially, it utilizes a **Safe Execution Layer**. Instead of aggressively patching production tables, it tests its AI-generated theories locally by dry-running database indices within locked transaction blocks (`BEGIN...ROLLBACK`). Because of this, it validates performance improvements autonomously, guaranteeing metrics like "percentage-based workload reductions" before a human engineer ever touches a button.

Everything operates across three paradigms:
- **Invisible background daemon** (`scheduler/monitor.py`)
- **Interactive frontend** (`app.py` Streamlit dashboard)
- **API protocol** designed natively for Claude AI Desktop integration (`mcp_server/server.py`)

---

## 🏗️ System Workflow & Architecture

The system seamlessly combines **Model Context Protocol (MCP)**, real-time database monitoring, advanced AI integration (Groq), and a safe execution layer to validate AI theories securely.

### System Architecture Overview
<img width="843" height="815" alt="image" src="https://github.com/user-attachments/assets/15986b7b-15f2-4f95-abfe-dd7f1c08af9a" />

### Agent Integration Architecture

<img width="843" height="815" alt="image" src="https://github.com/user-attachments/assets/9c6159ae-6da7-4f6e-a82f-b9f0ab2af344" />


### Five Core Workflow Layers

#### 1. 🔴 Real-Time Threat Trigger (The Capture Layer)

A silent background Python worker (`scheduler/monitor.py`) polls PostgreSQL's `pg_stat_statements` every few minutes. If a query suddenly averages longer than **500ms**, the system bypasses its batch cycle and dynamically isolates the query for an immediate AI health review.

#### 2. 🧠 EXPLAIN ANALYZE Extraction (The Intelligence Layer)

Once flagged, the system actively queries the database for the exact unoptimized query's internal tree structure using `EXPLAIN (ANALYZE, BUFFERS)`. This low-level metric blueprint is piped to the **Groq AI Engine** (`core/ai/analyzer.py`), stripping away hallucination by providing the AI with accurate, objective execution bottlenecks. It returns a JSON structure containing:
- Root cause analysis
- Optimized query rewrite
- Index suggestions

#### 3. 🛡️ Safe Execution Layer (The Validation Layer)

The AI proposes a complete schema restructuring. The agent intercepts this inside `core/db/queries.py` and runs a **Safe Validation**:

```sql
BEGIN;                          -- Start an isolated transaction block
CREATE INDEX...                 -- Test the AI's idea
-- Extract the new reduced Cost Metric
-- Automatically calculate the 🚀 Performance Improvement %
ROLLBACK;                       -- Completely revert the sandbox changes
```

This produces **verifiable, data-proven metrics** before recommending the solution permanently.

#### 4. 📊 Dashboard Visualization (The UI Layer)

All identified bottlenecks and their calculated percentage improvements are persisted cleanly inside a local SQLite knowledge-base (`data/recommendations.db`). This powers the **Premium Streamlit Dashboard** (`app.py`), which maps high-impact performance disruptions to:
- Dynamic bar charts
- Explicit AI analyses
- Real-time metrics
- Interactive visualizations

#### 5. 🔌 Model Context Protocol (The Integration Layer)

A distinct **FastMCP architecture** allows external clients, explicitly the standalone Claude Desktop App, to interact securely with the agent. By hooking Claude Desktop into this Python interface (`mcp_server/server.py`), external users can remotely command the agent via chat to:

```python
list_slow_queries()
analyze_query_performance(query_id)
show_db_health()
read_agent_logs(lines)
```

---

## 🔗 Understanding MCP Architecture & Claude Desktop Integration

### Claude Agent Workflow (Observe → Think → Act)

<img width="843" height="815" alt="image" src="https://github.com/user-attachments/assets/d985ce18-ea7d-41a2-884b-8c52b3732756" />


The diagram above illustrates how Claude Sonnet 4.6 processes your requests through three core cycles:

1. **Observe** - Reads your user intent and current context
2. **Think / Plan** - Determines which MCP tools to call and in what order
3. **Act** - Executes the selected tools via the MCP server

This loop repeats until Claude synthesizes a complete answer for you.

### 1. Claude Desktop is the MCP Client

In the Model Context Protocol architecture, **Claude Desktop App *is* the MCP Client.**

We don't need to write a client because Anthropic already built one and embedded it directly into their Claude application. The entire point of MCP is to let established AI assistants (like Claude) securely look into your local machine.

Our project only needs an **MCP Server** (`mcp_server/server.py`). Our server acts like a menu. It "advertises" your database tools like `list_slow_queries` to the outside world. When you open Claude Desktop, Claude acts as the **Client**, reads that menu, and decides when to execute those tools during your chat.

### 2. Where is the connection that links Claude to this codebase?

Because Claude is the client, the physical "connection wire" is actually configured **inside Claude Desktop itself**, not inside our Python repository.

If you open the `README.md` (under "Setup Instructions → 3. Expose the Agent Tools to Claude"), you will see this configuration block:

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

#### Here is exactly how the connection flows:

1. **Configuration**: You put that JSON block into Claude Desktop's configuration file (usually located at `%APPDATA%\Claude\claude_desktop_config.json` on Windows, or `~/.claude/claude_desktop_config.json` on macOS/Linux).

2. **Initialization**: When you start Claude Desktop, it reads that JSON file.

3. **Server Launch**: Claude Desktop silently runs the `command` provided, effectively launching your `mcp_server/server.py` file in the background.

4. **Communication**: Claude then communicates directly with `server.py` through **standard input/output streams (stdio)**.

### 3. How does the MCP server talk to your Database?

Once Claude commands your `server.py` to do something (like "What is the database health?"), the server needs to actually look at your PostgreSQL database.

If you look inside `mcp_server/server.py`, around **Line 41**, you'll see the connection bridging to your actual database logic:

```python
# ── Core Logic Dependencies ──────────────────────────────────────────────────
from core.db.postgres import db_manager
from core.db.queries import fetch_slow_queries, get_table_stats
```

When Claude triggers a tool (for example, `@mcp.tool() def show_db_health()`), that function uses `db_manager.test_connection()` internally. `db_manager` gets its connection strings (Username, Password, Port) directly from your **`.env`** file.

#### Summary of the Pipeline:

```
[You Chatting] 
    ↓
[Claude Desktop (The Client)] 
    ↓
[mcp_server/server.py (The Server)] 
    ↓
[.env (Credentials)] 
    ↓
[PostgreSQL (The Database)]
```

### Complete End-to-End User Query Flow
<img width="843" height="815" alt="image" src="https://github.com/user-attachments/assets/9f214a79-f6b1-45b5-957e-dd9eec8f5cc0" />


The diagram above shows the complete journey of a user query from initial question to final answer:

1. **User Query** - You ask Claude: "Which queries are impacting my database?"
2. **Claude AI Decision** - Claude understands your intent and decides which MCP tools to invoke
3. **MCP Server Execution** - The Autonomous DBA server executes three primary tools:
   - `list_slow_queries()` - Retrieves slow queries from pg_stat_statements
   - `analyze_query_performance()` - Performs deep analysis
   - `show_db_health()` - Returns database health metrics
4. **PostgreSQL Analysis** - pg_stat_statements data is extracted and analyzed
5. **AI Analysis Engine** - EXPLAIN/EXPLAIN ANALYZE is executed on flagged queries to identify:
   - Missing indices
   - Full table scans
   - Query plan inefficiencies
6. **Claude Synthesis** - Claude interprets the findings and translates them into actionable recommendations
7. **Your Answer** - You receive:
   - Visual charts of query performance
   - Detailed tables of results
   - Plain-language explanations
   - Specific optimization recommendations

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend Infrastructure** | Python 3.12, APScheduler (Daemons) |
| **Database Architecture** | PostgreSQL (psycopg2, pg_stat_statements) |
| **LLM Agent Inference** | Groq API SDK (High-Speed LLaMA Models) |
| **Local Analytics Storage** | SQLite + SQLAlchemy |
| **Interactive UI Dashboard** | Streamlit + Plotly (Dark Mode/Premium Layouts) |
| **Client Protocol Exposer** | Model Context Protocol Server (FastMCP) |

---

## 🚀 Setup Instructions

### 1. Environment Setup

To set up this workspace locally, you need **Python 3.12** (or higher) and a running instance of **PostgreSQL**.

#### Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows WSL/Linux/macOS
# On Windows PowerShell: .\venv\Scripts\Activate.ps1
```

#### Install the dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configuration (.env)

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

1. **Connect to your database**
2. **Run the following command:**

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

---

## 🏃 Execution Steps

The architecture is multi-faceted. You can run individual components based on your current need. **Ensure your virtual environment is active before running.**

### 1. Run the Dashboard (Streamlit)

To visualize identified optimizations, AI metrics, and trigger tasks manually:

```bash
streamlit run app.py
```

This boots up a premium Web UI dynamically hosted at **http://localhost:8501**.

### 2. Start the Real-Time Background Monitor

To enable the agent to act purely autonomously in the background (capturing spikes and generating Groq insights without human interaction):

```bash
python -m scheduler.monitor
```

**Note:** This runs infinitely in the terminal daemon until you press `Ctrl+C`.

### 3. Expose the Agent Tools to Claude (MCP Server)

If you want to plug the optimization tools directly into Claude Desktop using the Model Context Protocol:

#### Step A: Configure Claude Desktop

Add the following to your Claude Desktop configuration file:

**On Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**On macOS/Linux:** `~/.claude/claude_desktop_config.json`

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

**Replace `/absolute/path/to/slow query ai agent/` with your actual project directory path.**

#### Step B: Restart Claude Desktop

Close and reopen Claude Desktop completely. It will now automatically load your MCP server.

#### Step C: Start Using the Tools

You can now ask Claude questions like:
- "What queries are currently running slow in my database?"
- "Show me the database health metrics"
- "What optimizations do you recommend for my slow queries?"

Claude will invoke the local Python server internally and return the results.

---

## 📊 Project Structure

```
slow-query-ai-agent/
├── app.py                          # Streamlit dashboard
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .env                            # Configuration (create from .env.example)
│
├── scheduler/
│   └── monitor.py                  # Background query monitoring daemon
│
├── mcp_server/
│   └── server.py                   # FastMCP server for Claude integration
│
├── core/
│   ├── ai/
│   │   └── analyzer.py             # Groq LLM integration & analysis
│   ├── db/
│   │   ├── postgres.py             # PostgreSQL connection manager
│   │   └── queries.py              # Safe query execution & validation
│   └── utils/
│       └── logger.py               # Logging utilities
│
└── data/
    └── recommendations.db          # SQLite knowledge base
```

---

## 🎯 Key Features

✅ **Real-time Monitoring** - Continuous polling of slow queries via `pg_stat_statements`  
✅ **AI-Powered Analysis** - Groq LLaMA models for intelligent optimization suggestions  
✅ **Safe Execution** - Transaction-based testing without affecting production  
✅ **Performance Validation** - Automatic metrics calculation before implementation  
✅ **Interactive Dashboard** - Premium Streamlit UI with Plotly visualizations  
✅ **Claude Integration** - Native MCP support for Claude Desktop integration  
✅ **Autonomous Operation** - Runs completely independently in the background  

---

## 🔐 Safety & Security

- **Transaction Isolation**: All tests run in `BEGIN...ROLLBACK` blocks
- **No Direct Production Changes**: All recommendations are validated before implementation
- **Credential Management**: Sensitive data stored in `.env` (never committed to version control)
- **MCP Protocol Security**: Encrypted communication between Claude and local server

---

## 📝 License

This project is open-source and available under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

## ❓ FAQ

**Q: Can this accidentally modify my production database?**  
A: No. All optimizations are tested in isolated transactions that are automatically rolled back.

**Q: Do I need to run all three components (Monitor, Dashboard, MCP Server)?**  
A: No. You can run them independently based on your needs. The Monitor runs autonomously, the Dashboard for visualization, and the MCP Server for Claude integration.

**Q: What if the Groq API is down?**  
A: The system will log the error and continue monitoring. Analysis will resume once the API is available.

**Q: Can I use this with other databases besides PostgreSQL?**  
A: Currently, this project is built specifically for PostgreSQL. Support for other databases would require modifications to the core connection and query analysis logic.

---

## 📞 Support

For issues, questions, or feature requests, please open an issue on the project repository.
