import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from models.topic import Topic, UserTopicProgress

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/placement", tags=["placement"])


class CreateUserRequest(BaseModel):
    name: str


@router.post("/user")
def create_user(req: CreateUserRequest, db: Session = Depends(get_db)):
    user = User(name=req.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "name": user.name}


@router.get("/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.id, "name": user.name, "total_xp": user.total_xp, "streak_days": user.streak_days}
