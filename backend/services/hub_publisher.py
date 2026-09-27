"""INT-2 (ACTION_PLAN F5.2): outbound event queue to the System-Główny hub.

queue_event() writes a row next to the user's own change; flush_pending() sends
unsent rows and never raises - a hub that is down only leaves them queued.
Config is read from backend/.env by absolute path (the app's Settings use a
cwd-relative ".env", which silently misses the key when started from the repo root).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import Session

from backend.models.outbound_event import OutboundEvent

MODULE_NAME = "hackerlab-academy"
MAX_ATTEMPTS = 20


class HubSettings(BaseSettings):
    SYSTEM_GLOWNY_URL: str = "http://localhost:8000"
    SYSTEM_GLOWNY_MODULE_KEY: str = ""

    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[1] / ".env", extra="ignore")


hub_settings = HubSettings()


def queue_event(db: Session, event_type: str, user_id, data: dict, **extra) -> OutboundEvent:
    """Add an event to the queue. The caller commits (same transaction as its change)."""
    payload = {
        "event_type": event_type,
        "module": MODULE_NAME,
        "user_id": str(user_id),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
        **extra,
    }
    row = OutboundEvent(event_type=event_type, user_id=str(user_id), payload_json=json.dumps(payload))
    db.add(row)
    return row


def flush_pending(db: Session, limit: int = 50) -> int:
    if not hub_settings.SYSTEM_GLOWNY_MODULE_KEY:
        return 0  # integration not configured - keep the queue, send nothing
    pending = (
        db.query(OutboundEvent)
        .filter(OutboundEvent.sent_at.is_(None), OutboundEvent.attempts < MAX_ATTEMPTS)
        .order_by(OutboundEvent.id)
        .limit(limit)
        .all()
    )
    sent = 0
    for row in pending:
        try:
            resp = httpx.post(
                f"{hub_settings.SYSTEM_GLOWNY_URL}/api/v1/integrations/event",
                json=json.loads(row.payload_json),
                headers={"X-Module-Key": hub_settings.SYSTEM_GLOWNY_MODULE_KEY},
                timeout=5.0,
            )
            if resp.status_code < 300:
                row.sent_at = datetime.utcnow()
                sent += 1
            else:
                row.attempts += 1
        except httpx.HTTPError:
            row.attempts += 1
        db.commit()
    return sent


def flush_in_background() -> int:
    """For BackgroundTasks: own session, request session is already closed."""
    from backend import database  # resolved at call time (tests swap SessionLocal)

    db = database.SessionLocal()
    try:
        return flush_pending(db)
    finally:
        db.close()
