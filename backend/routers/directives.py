"""INT-3 (ACTION_PLAN F5.3): directives from the System-Główny hub.

Hub contract: {"directive", "enabled", "value", "from", "to"}. survival_mode
shrinks the daily agenda (brain) to one 5-minute flashcard session.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.directive_state import DirectiveState

router = APIRouter(prefix="/directives", tags=["Directives"])

KNOWN = {"survival_mode", "priority", "quiet_hours"}


class DirectivePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    directive: str
    user_id: int = 1  # single-user today
    enabled: bool | None = None
    value: str | None = None
    from_: str | None = Field(None, alias="from")
    to: str | None = None


def get_state(db: Session, user_id: int) -> DirectiveState | None:
    return db.query(DirectiveState).filter(DirectiveState.user_id == user_id).first()


@router.post("")
def apply_directive(payload: DirectivePayload, db: Session = Depends(get_db)):
    if payload.directive not in KNOWN:
        raise HTTPException(status_code=422, detail=f"Unknown directive: {payload.directive}")
    state = get_state(db, payload.user_id)
    if not state:
        state = DirectiveState(user_id=payload.user_id)
        db.add(state)
    if payload.directive == "survival_mode":
        state.survival_mode = bool(payload.enabled)
    elif payload.directive == "priority":
        state.priority_topic = payload.value if payload.enabled is not False else None
    else:
        on = payload.enabled is not False
        state.quiet_hours_from = payload.from_ if on else None
        state.quiet_hours_to = payload.to if on else None
    db.commit()
    return {"status": "applied", "directive": payload.directive}


@router.get("/{user_id}")
def directive_status(user_id: int, db: Session = Depends(get_db)):
    s = get_state(db, user_id)
    return {
        "survival_mode": bool(s and s.survival_mode),
        "priority_topic": s.priority_topic if s else None,
        "quiet_hours": {"from": s.quiet_hours_from, "to": s.quiet_hours_to} if s and s.quiet_hours_from else None,
    }
