"""
core/ai/analyzer.py
-------------------
AI Agent core for query analysis using Groq.
"""
from __future__ import annotations

import json
from typing import Any

from groq import Groq

from core.config import settings
from core.db.queries import get_explain_plan, dry_run_index
from core.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from core.logging_config import logger

class AIAnalyzer:
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self._client = None

    @property
    def client(self) -> Groq:
        if self._client is None:
            if not self.api_key:
                raise ValueError("GROQ_API_KEY is not set.")
            self._client = Groq(api_key=self.api_key)
        return self._client

    def analyze(self, query_data: dict[str, Any]) -> dict[str, Any]:
        """
        Deep analysis: Fetch EXPLAIN plan, then ask LLM for tuning.
        """
        query_text = query_data["query"]
        queryid = query_data["queryid"]
        
        # Step 1: Get EXPLAIN plan automatically
        logger.info(f"Generating EXPLAIN plan for query {queryid}...")
        explain_plan = get_explain_plan(query_text)
        
        # Step 2: Build Prompt
        prompt = USER_PROMPT_TEMPLATE.format(
            query_text=query_text,
            calls=query_data.get("calls", "Unknown"),
            mean_exec_time=query_data.get("mean_exec_time", "Unknown"),
            total_impact_pct=round(query_data.get("total_impact_pct", 0.0), 2),
            explain_plan=explain_plan
        )
        
        try:
            logger.info(f"Sending query {queryid} to Groq ({self.model})...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Step 3: SAFE EXECUTION LAYER & METRICS TRACKING
            # Run dry run index to validate the suggestion and get the metric baseline
            index_sql = result.get("index_suggestion", "None")
            if index_sql and index_sql.strip().upper() != "NONE" and "CREATE" in index_sql.upper():
                logger.info("Executing Safe Dry-Run for suggested index...")
                dry_run_result = dry_run_index(index_sql, query_text)
                if dry_run_result.get("success"):
                    result["analysis"] += f"\n\n[DRY RUN SAFE VALIDATION]: Validated safely. Performance improvement baseline calculated at {dry_run_result['improvement_pct']:.2f}%."
                else:
                    result["analysis"] += f"\n\n[DRY RUN SAFE VALIDATION]: Failed to validate - {dry_run_result.get('message')}."
                    
            logger.info(f"Analysis complete for {queryid}")
            return result
            
        except Exception as e:
            logger.error(f"AI analysis failed for {queryid}: {e}")
            return {
                "analysis": f"Error during AI analysis: {str(e)}",
                "rewritten_query": "N/A",
                "index_suggestion": "None",
                "confidence_score": 0.0
            }

analyzer = AIAnalyzer()
