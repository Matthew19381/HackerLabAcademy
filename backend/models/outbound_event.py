from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from backend.database import Base


class OutboundEvent(Base):
    """Events waiting to be sent to the System-Główny hub (INT-2, ACTION_PLAN F5.2).

    Queued in the same transaction as the user's action, sent best-effort; a hub
    that is down only leaves rows with sent_at = NULL for the next flush.
    """

    __tablename__ = "outbound_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    user_id = Column(String, nullable=False, index=True)
    payload_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    sent_at = Column(DateTime, nullable=True)
    attempts = Column(Integer, default=0)
