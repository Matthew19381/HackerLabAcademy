from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.exercise_service import (
    generate_exercises_for_topic,
    get_exercises_for_topic,
    submit_exercise_answer,
)
from backend.models.exercise import Exercise

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


@router.post("/topics/{topic_id}/generate")
async def generate_exercises(topic_id: int, count: int = 5, db: Session = Depends(get_db)):
    """Generate exercises for a topic using AI."""
    try:
        exercises = await generate_exercises_for_topic(topic_id, db, count)
        return [
            {
                "id": ex.id,
                "type": ex.exercise_type,
                "question": ex.question,
                "options": json.loads(ex.options) if ex.options else None,
                "code_snippet": ex.code_snippet,
                "difficulty": ex.difficulty,
                "explanation": ex.explanation,
            }
            for ex in exercises
        ]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics/{topic_id}")
def list_exercises(topic_id: int, db: Session = Depends(get_db)):
    """List all exercises for a topic."""
    exercises = get_exercises_for_topic(topic_id, db)
    return [
        {
            "id": ex.id,
            "type": ex.exercise_type,
            "question": ex.question,
            "options": json.loads(ex.options) if ex.options else None,
            "code_snippet": ex.code_snippet,
            "difficulty": ex.difficulty,
            "explanation": ex.explanation,
        }
        for ex in exercises
    ]


@router.post("/submit")
def submit_answer(
    exercise_id: int,
    user_id: int,
    user_answer: str,
    db: Session = Depends(get_db),
):
    """Submit an answer to an exercise."""
    try:
        result = submit_exercise_answer(user_id, exercise_id, user_answer, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
