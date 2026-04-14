"""
core/store/repository.py
------------------------
Repository pattern for QueryRecommendation entities.
"""
from __future__ import annotations

import datetime
from typing import Any
from core.store.database import get_session, QueryRecommendation
from core.logging_config import logger

class RecommendationRepository:
    
    @staticmethod
    def upsert_query_meta(query_data: dict[str, Any]) -> None:
        """Saves or updates query metadata (before AI analysis)."""
        session = get_session()
        try:
            existing = session.query(QueryRecommendation).filter_by(
                queryid=query_data["queryid"]
            ).first()
            
            now = datetime.datetime.now(datetime.timezone.utc)
            if existing:
                existing.calls = query_data.get("calls", existing.calls)
                existing.mean_exec_time = query_data.get("mean_exec_time", existing.mean_exec_time)
                existing.total_impact_pct = query_data.get("total_impact_pct", existing.total_impact_pct)
                existing.last_seen_at = now
            else:
                rec = QueryRecommendation(
                    queryid=query_data["queryid"],
                    original_query=query_data["query"],
                    calls=query_data.get("calls"),
                    mean_exec_time=query_data.get("mean_exec_time"),
                    total_impact_pct=query_data.get("total_impact_pct"),
                    last_seen_at=now
                )
                session.add(rec)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Upsert query meta failed: {e}")
        finally:
            session.close()

    @staticmethod
    def save_ai_analysis(queryid: str, ai_result: dict[str, Any]) -> bool:
        """Saves AI analysis results to an existing query record."""
        session = get_session()
        try:
            existing = session.query(QueryRecommendation).filter_by(queryid=queryid).first()
            if not existing:
                logger.warning(f"Attempted to save analysis for unknown queryid {queryid}")
                return False
            
            existing.analysis = ai_result.get("analysis")
            existing.rewritten_query = ai_result.get("rewritten_query")
            existing.index_suggestion = ai_result.get("index_suggestion")
            existing.confidence_score = ai_result.get("confidence_score", 0.0)
            existing.analyzed_at = datetime.datetime.now(datetime.timezone.utc)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Save AI analysis failed: {e}")
            return False
        finally:
            session.close()

    @staticmethod
    def get_all(limit: int = 100) -> list[QueryRecommendation]:
        session = get_session()
        try:
            return session.query(QueryRecommendation).order_by(QueryRecommendation.mean_exec_time.desc()).limit(limit).all()
        finally:
            session.close()

    @staticmethod
    def get_by_id(queryid: str) -> QueryRecommendation | None:
        session = get_session()
        try:
            return session.query(QueryRecommendation).filter_by(queryid=queryid).first()
        finally:
            session.close()
            
    @staticmethod
    def delete(queryid: str) -> bool:
        session = get_session()
        try:
            row = session.query(QueryRecommendation).filter_by(queryid=queryid).first()
            if row:
                session.delete(row)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Delete recommendation failed: {e}")
            return False
        finally:
            session.close()

repo = RecommendationRepository()
