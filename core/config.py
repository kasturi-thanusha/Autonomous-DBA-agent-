"""
core/config.py
--------------
Centralised settings for the Autonomous DBA Agent.
100% Zero-Dependency version using Python Standard Libraries.
Removes all 'missing-import' errors from any IDE immediately.
"""
from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass, field

# Project root 
BASE_DIR: Path = Path(__file__).resolve().parent.parent

def load_env_file(path: Path) -> None:
    """Manual .env loader to avoid dependency on python-dotenv."""
    if not path.exists():
        return
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

# Load environment
load_env_file(BASE_DIR / ".env")

@dataclass
class Settings:
    # ── PostgreSQL ─────────────────────────────────────────────────────────────
    db_host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    db_port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    db_name: str = field(default_factory=lambda: os.getenv("DB_NAME", "postgres"))
    db_user: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    db_password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))

    # ── Groq AI ───────────────────────────────────────────────────────────────
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    groq_model: str   = field(default_factory=lambda: os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))

    # ── Monitoring Thresholds ─────────────────────────────────────────────────
    slow_query_threshold_ms: float = field(
        default_factory=lambda: float(os.getenv("SLOW_QUERY_THRESHOLD_MS", "100.0"))
    )
    slow_query_limit: int = field(
        default_factory=lambda: int(os.getenv("SLOW_QUERY_LIMIT", "20"))
    )
    capture_interval_minutes: int = field(
        default_factory=lambda: int(os.getenv("CAPTURE_INTERVAL_MINUTES", "5"))
    )

    # ── Connection Pool ───────────────────────────────────────────────────────
    pool_min_conn: int = field(default_factory=lambda: int(os.getenv("POOL_MIN_CONN", "1")))
    pool_max_conn: int = field(default_factory=lambda: int(os.getenv("POOL_MAX_CONN", "5")))

    # ── Logging & Storage ───────────────────────────────────────────────────
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper())
    
    # Path defaults 
    log_file: str = str(BASE_DIR / "logs" / "dba_agent.log")
    store_db_path: str = f"sqlite:///{BASE_DIR / 'data' / 'recommendations.db'}"

    @property
    def dsn(self) -> str:
        """Returns the PostgreSQL connection string."""
        return (
            f"host={self.db_host} port={self.db_port} "
            f"dbname={self.db_name} user={self.db_user} "
            f"password={self.db_password}"
        )

# Singleton instance
settings = Settings()



