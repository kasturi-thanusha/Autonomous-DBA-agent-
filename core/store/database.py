"""
core/store/database.py
----------------------
SQLAlchemy models and session management for the recommendation store.
"""
from __future__ import annotations

import datetime
from pathlib import Path

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings
from core.logging_config import logger

Base = declarative_base()

class QueryRecommendation(Base):
    __tablename__ = "query_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    queryid = Column(String(100), unique=True, index=True, nullable=False)
    original_query = Column(Text, nullable=False)
    calls = Column(Integer)
    mean_exec_time = Column(Float)
    total_impact_pct = Column(Float)
    
    # AI Output
    analysis = Column(Text)
    rewritten_query = Column(Text)
    index_suggestion = Column(Text)
    confidence_score = Column(Float, default=0.0)
    
    analyzed_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_seen_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

# Global engine and session factory
_engine = None
_SessionFactory = None

def init_store():
    global _engine, _SessionFactory
    
    # Ensure data directory exists
    db_url = settings.store_db_path
    if db_url.startswith("sqlite:///"):
        db_path = Path(db_url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
    logger.info(f"Initializing SQLite store at {db_url}")
    _engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(_engine)

    _SessionFactory = sessionmaker(bind=_engine)

def get_session():
    if _SessionFactory is None:
        init_store()
    return _SessionFactory()
