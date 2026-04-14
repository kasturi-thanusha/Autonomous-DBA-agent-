"""
core/db/postgres.py
-------------------
Thread-safe PostgreSQL connection pooling using psycopg2.
Ensures we don't leak connections in a multi-threaded MCP/Streamlit environment.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from psycopg2 import pool
from psycopg2.extensions import connection, cursor

from core.config import settings
from core.logging_config import logger

class PostgresManager:
    _pool: pool.ThreadedConnectionPool | None = None

    @classmethod
    def get_pool(cls) -> pool.ThreadedConnectionPool:
        if cls._pool is None:
            try:
                logger.debug("Initializing PostgreSQL connection pool...")
                cls._pool = pool.ThreadedConnectionPool(
                    minconn=settings.pool_min_conn,
                    maxconn=settings.pool_max_conn,
                    dsn=settings.dsn
                )
            except Exception as e:
                logger.error(f"Failed to initialize Postgres pool: {e}")
                raise
        return cls._pool

    @classmethod
    @contextmanager
    def get_connection(cls) -> Generator[connection, None, None]:
        p = cls.get_pool()
        conn = p.getconn()
        try:
            yield conn
        finally:
            # Important: always return the connection to the pool
            p.putconn(conn)

    @classmethod
    @contextmanager
    def get_cursor(cls) -> Generator[cursor, None, None]:
        with cls.get_connection() as conn:
            with conn.cursor() as cur:
                yield cur

    @classmethod
    def test_connection(cls) -> bool:
        """Ping-like check."""
        try:
            with cls.get_cursor() as cur:
                cur.execute("SELECT 1")
                return True
        except Exception as e:
            logger.warning(f"Postgres health check failed: {e}")
            return False

db_manager = PostgresManager()
