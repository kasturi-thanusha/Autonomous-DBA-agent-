"""
core/logging_config.py
----------------------
Structured logger: human-readable stderr + JSON-newline file output.
Import `logger` from this module everywhere else.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


class _JSONFormatter(logging.Formatter):
    """Emit each log record as a single JSON line (NDJSON)."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "ts":       datetime.now(timezone.utc).isoformat(),
            "level":    record.levelname,
            "logger":   record.name,
            "msg":      record.getMessage(),
            "module":   record.module,
            "func":     record.funcName,
            "line":     record.lineno,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra"):
            payload.update(record.extra)  # type: ignore[arg-type]
        return json.dumps(payload, default=str)


def setup_logging() -> logging.Logger:
    # Lazy import to avoid circular deps at module load time
    from core.config import settings  # noqa: PLC0415

    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(getattr(logging, settings.log_level, logging.INFO))

    if not root.handlers:
        # ── stderr: human-friendly ─────────────────────────────────────────
        sh = logging.StreamHandler(sys.stderr)
        sh.setFormatter(
            logging.Formatter(
                "%(asctime)s  %(levelname)-8s  %(name)-24s  %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root.addHandler(sh)

        # ── file: JSON structured ──────────────────────────────────────────
        fh = logging.FileHandler(log_path, encoding="utf-8")
        fh.setFormatter(_JSONFormatter())
        root.addHandler(fh)

    return logging.getLogger("dba_agent")


logger = setup_logging()
