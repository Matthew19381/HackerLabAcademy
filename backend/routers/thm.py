"""TryHackMe tracker (plan C4/C7): rooms and paths entered by hand, done / not done, notes.

No XP and no ranking (decision 2 of 2026-08-09). Marking an entry done queues a
`thm_room_completed` / `thm_path_completed` event for the System-Glowny hub.
"""
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.thm_progress import ThmProgress
from backend.models.user import User
from backend.services.hub_publisher import flush_in_background, queue_event

router = APIRouter(prefix="/thm", tags=["tryhackme"])


class ThmCreate(BaseModel):
    user_id: int
    kind: Literal["room", "path"] = "room"
    name: str = Field(min_length=1, max_length=200)
    url: str | None = Field(None, max_length=500)
    category: str | None = Field(None, max_length=60)
    notes: str | None = None


class ThmUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    url: str | None = Field(None, max_length=500)
    category: str | None = Field(None, max_length=60)
    notes: str | None = None
    done: bool | None = None


def _out(row: ThmProgress) -> dict:
    return {
        "id": row.id,
        "kind": row.kind,
        "name": row.name,
        "url": row.url,
        "category": row.category,
        "done": bool(row.done),
        "completed_at": row.completed_at.isoformat() if row.completed_at else None,
        "notes": row.notes,
    }


def _get(db: Session, entry_id: int) -> ThmProgress:
    row = db.get(ThmProgress, entry_id)
    if not row:
        raise HTTPException(status_code=404, detail="Nie ma takiego wpisu")
    return row


@router.get("")
def list_entries(user_id: int = Query(...), done: bool | None = None, db: Session = Depends(get_db)):
    query = db.query(ThmProgress).filter(ThmProgress.user_id == user_id)
    if done is not None:
        query = query.filter(ThmProgress.done.is_(done))
    rows = query.order_by(ThmProgress.done, ThmProgress.completed_at.desc(), ThmProgress.id.desc()).all()
    return {
        "entries": [_out(r) for r in rows],
        "counts": {"done": sum(1 for r in rows if r.done), "todo": sum(1 for r in rows if not r.done)},
    }


@router.post("", status_code=201)
def create_entry(req: ThmCreate, db: Session = Depends(get_db)):
    if not db.get(User, req.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    row = ThmProgress(**req.model_dump(), done=False)
    db.add(row)
    db.commit()
    db.refresh(row)
    return _out(row)


@router.patch("/{entry_id}")
def update_entry(entry_id: int, req: ThmUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    row = _get(db, entry_id)
    changes = req.model_dump(exclude_unset=True)
    became_done = changes.get("done") is True and not row.done
    for field, value in changes.items():
        setattr(row, field, value)
    if "done" in changes:
        row.completed_at = datetime.utcnow() if row.done else None
    if became_done:
        queue_event(db, f"thm_{row.kind}_completed", row.user_id,
                    {"thm_id": row.id, "name": row.name, "category": row.category}, tags=["learning"])
    db.commit()
    if became_done:
        background_tasks.add_task(flush_in_background)
    return _out(row)


@router.delete("/{entry_id}")
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    db.delete(_get(db, entry_id))
    db.commit()
    return {"success": True}
