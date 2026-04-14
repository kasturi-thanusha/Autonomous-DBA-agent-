# Autonomous AI DBA Agent - Setup Instructions

## 1. Environment Setup
To set up this workspace locally, you need Python 3.12 (or higher) and a running instance of PostgreSQL.

**Create and activate a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows WSL/Linux
```

**Install the dependencies:**
```bash
pip install -r requirements.txt
```

## 2. Configuration (`.env`)
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

## 3. Database Preparation
Ensure your PostgreSQL database has the `pg_stat_statements` extension enabled. This allows the AI agent to capture slow queries natively:
1. Connect to your database.
2. Run: `CREATE EXTENSION IF NOT EXISTS pg_stat_statements;`
