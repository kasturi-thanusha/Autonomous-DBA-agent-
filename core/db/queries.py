"""
core/db/queries.py
------------------
High-level PostgreSQL operations for DBA tasks.
"""
from __future__ import annotations

from typing import Any
from core.db.postgres import db_manager
from core.config import settings
from core.logging_config import logger

def fetch_slow_queries(limit: int | None = None, min_time_ms: float | None = None) -> list[dict[str, Any]]:
    """
    Fetch slow queries from pg_stat_statements.
    """
    limit = limit or settings.slow_query_limit
    threshold = min_time_ms if min_time_ms is not None else settings.slow_query_threshold_ms

    sql = """
        SELECT
            queryid::text,
            query,
            calls,
            total_exec_time,
            mean_exec_time,
            rows,
            (total_exec_time / SUM(total_exec_time) OVER()) * 100 as total_impact_pct
        FROM pg_stat_statements
        WHERE mean_exec_time > %s
          AND query NOT LIKE '%%pg_stat_statements%%'
          AND query NOT LIKE '%%EXPLAIN%%'
        ORDER BY mean_exec_time DESC
        LIMIT %s;
    """
    
    try:
        with db_manager.get_cursor() as cur:
            cur.execute(sql, (threshold, limit))
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            
            results = [dict(zip(columns, row)) for row in rows]
            logger.info(f"Fetched {len(results)} slow queries above {threshold}ms")
            return results
    except Exception as e:
        logger.error(f"Error fetching slow queries: {e}")
def get_explain_plan(query: str) -> str:
    """
    Executes EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON) for a query.
    Note: RUN WITH CAUTION. DO NOT RUN ON DESTRUCTIVE QUERIES.
    """
    clean_query = query.strip().upper()
    if not clean_query.startswith("SELECT"):
        return "EXPLAIN only supported for SELECT queries for safety."

    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS) {query}"
    
    try:
        with db_manager.get_cursor() as cur:
            cur.execute(explain_sql)
            plan_rows = cur.fetchall()
            return "\n".join([r[0] for r in plan_rows])
    except Exception as e:
        logger.error(f"Error running EXPLAIN: {e}")
        return f"Error: {e}"

def dry_run_index(index_sql: str, original_query: str) -> dict[str, Any]:
    """
    SAFE EXECUTION LAYER:
    Applies the index in a transaction, evaluates the new EXPLAIN cost to calculate
    Metrics Tracking (Improvement %), and then performs a ROLLBACK.
    """
    if "CONCURRENTLY" in index_sql.upper():
        index_sql = index_sql.replace("CONCURRENTLY", "")
        
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Baseline cost
                cur.execute(f"EXPLAIN (FORMAT JSON) {original_query}")
                baseline_plan = cur.fetchone()[0]
                baseline_cost = baseline_plan[0]['Plan']['Total Cost']

                # 2. Dry run with transaction rollback
                try:
                    cur.execute("BEGIN;")
                    cur.execute(index_sql)
                    
                    cur.execute(f"EXPLAIN (FORMAT JSON) {original_query}")
                    new_plan = cur.fetchone()[0]
                    new_cost = new_plan[0]['Plan']['Total Cost']
                finally:
                    cur.execute("ROLLBACK;")
                
                improvement_pct = 0.0
                if baseline_cost > 0:
                    improvement_pct = ((baseline_cost - new_cost) / baseline_cost) * 100
                    
                return {
                    "success": True,
                    "baseline_cost": baseline_cost,
                    "new_cost": new_cost,
                    "improvement_pct": improvement_pct,
                    "message": f"Dry-run executed safely. Improvement: {improvement_pct:.2f}%"
                }
    except Exception as e:
        logger.error(f"Safe execution failed: {e}")
        return {"success": False, "message": str(e)}

def get_table_stats() -> list[dict[str, Any]]:
    """Get largest tables and their bloat-related stats."""
    sql = """
        SELECT 
            relname as table_name,
            pg_size_pretty(pg_total_relation_size(relid)) as total_size,
            n_live_tup as row_count,
            n_dead_tup as dead_tuples,
            last_vacuum,
            last_analyze
        FROM pg_stat_user_tables
        ORDER BY pg_total_relation_size(relid) DESC
        LIMIT 10;
    """
    try:
        with db_manager.get_cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
    except Exception as e:
        logger.error(f"Error getting table stats: {e}")
        return []
