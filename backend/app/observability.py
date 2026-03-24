from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from .models import AuditLog


LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
APP_LOG_PATH = LOG_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(APP_LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("aspredictive")


def log_request_event(request: Request, status_code: int, duration_ms: float) -> None:
    logger.info(
        "request method=%s path=%s status=%s duration_ms=%.2f client=%s",
        request.method,
        request.url.path,
        status_code,
        duration_ms,
        request.client.host if request.client else "unknown",
    )


def write_audit_log(
    db: Session,
    *,
    actor_user_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details_json=json.dumps(details or {}, ensure_ascii=False),
    )
    db.add(entry)


def cleanup_expired_password_resets(db: Session, token_model: Any) -> int:
    now = datetime.utcnow()
    expired_tokens = db.query(token_model).filter(token_model.expires_at < now, token_model.used_at.is_(None)).all()
    count = len(expired_tokens)
    for token in expired_tokens:
        db.delete(token)
    return count


def generate_backup_filename(prefix: str = "aspredictive_backup") -> str:
    return f"{prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.sql"
