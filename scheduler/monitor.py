"""
scheduler/monitor.py
--------------------
Background daemon that periodically captures slow query metrics.
This makes the agent autonomous by building a history of performance trends.
"""
from __future__ import annotations

import time
from apscheduler.schedulers.background import BackgroundScheduler

from core.db.queries import fetch_slow_queries
from core.store.repository import repo
from core.store.database import init_store
from core.config import settings
from core.logging_config import logger

def capture_metrics_job():
    """Timer job to fetch slow queries and update the store."""
    try:
        logger.info("Autonomous Capture Cycle: Fetching slow queries...")
        queries = fetch_slow_queries()
        
        if not queries:
            logger.info("No slow queries found in this cycle.")
            return
            
        for q in queries:
            repo.upsert_query_meta(q)
            
            # 1. REAL-TIME TRIGGER: Auto trigger analysis if > 500ms limit
            if q.get("mean_exec_time", 0) > 500:
                logger.warning(f"🔴 REAL-TIME TRIGGER: Spike detected on {q['queryid']} ({q['mean_exec_time']:.1f}ms). Auto-triggering AI Analysis...")
                
                # Check if it was already analyzed recently
                existing_rec = repo.get_by_id(q['queryid'])
                if existing_rec and existing_rec.analysis:
                    continue # Skip if already analyzed
                    
                # Real-Time AI execution pipeline
                try:
                    from core.ai.analyzer import analyzer
                    result = analyzer.analyze(q)
                    repo.save_ai_analysis(q['queryid'], result)
                    logger.info(f"✅ Auto-Analysis complete for {q['queryid']}.")
                except Exception as eval_err:
                    logger.error(f"Failed AI Auto-Analysis for {q['queryid']}: {eval_err}")
                    
        logger.info(f"Capture Cycle Complete: Checked {len(queries)} records.")
    except Exception as e:
        logger.error(f"Error in capture_metrics_job: {e}")

def start_monitor():
    """Initialises and starts the background monitor."""
    init_store()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        capture_metrics_job, 
        'interval', 
        minutes=settings.capture_interval_minutes,
        id='db_monitor_job'
    )
    
    logger.info(f"Starting database monitor (interval: {settings.capture_interval_minutes}m)")
    scheduler.start()
    
    try:
        # Keep main thread alive if run standalone
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Database monitor stopped.")

if __name__ == "__main__":
    start_monitor()
