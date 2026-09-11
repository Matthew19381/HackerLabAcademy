import json
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models.user import User
from backend.models.topic import Topic, UserTopicProgress
from backend.models.flashcard import Flashcard
from backend.models.error_item import ErrorItem
from backend.services.lesson_service import generate_theory_lesson, generate_lab_instructions, analyze_quiz_errors
from backend.services.achievement_service import check_and_award_achievements, calculate_level_from_xp

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/topics", tags=["topics"])

XP_THEORY = 20
XP_QUIZ_PASS = 30
XP_LAB = 50


@router.get("/")
def get_all_topics(user_id: int, db: Session = Depends(get_db)):
    """Return all topics with user's progress and unlock status."""
    topics = db.query(Topic).order_by(Topic.order_index).all()
    progress_map = {}
    if user_id:
        progs = db.query(UserTopicProgress).filter(UserTopicProgress.user_id == user_id).all()
        progress_map = {p.topic_id: p for p in progs}

    result = []
    for t in topics:
        prereqs = json.loads(t.prerequisites or "[]")
        # Topic is unlocked if all prerequisites are completed (theory + quiz)
        unlocked = True
        for prereq_slug in prereqs:
            prereq_topic = db.query(Topic).filter(Topic.slug == prereq_slug).first()
            if prereq_topic:
                prereq_progress = progress_map.get(prereq_topic.id)
                if not prereq_progress or not prereq_progress.theory_completed:
                    unlocked = False
                    break

        prog = progress_map.get(t.id)
        result.append({
            "id": t.id,
            "slug": t.slug,
            "name": t.name,
            "category": t.category,
            "difficulty": t.difficulty,
            "description": t.description,
            "prerequisites": prereqs,
            "lab_type": t.lab_type,
            "order_index": t.order_index,
            "unlocked": unlocked,
            "theory_completed": prog.theory_completed if prog else False,
            "lab_completed": prog.lab_completed if prog else False,
            "quiz_score": prog.quiz_score if prog else None,
        })

    return result


@router.get("/{slug}/theory")
async def get_theory(slug: str, user_id: int, db: Session = Depends(get_db)):
    """Get (or generate) theory lesson for a topic."""
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Check prerequisites
    prereqs = json.loads(topic.prerequisites or "[]")
    if user_id and prereqs:
        for prereq_slug in prereqs:
            prereq_topic = db.query(Topic).filter(Topic.slug == prereq_slug).first()
            if prereq_topic:
                prog = db.query(UserTopicProgress).filter(
                    UserTopicProgress.user_id == user_id,
                    UserTopicProgress.topic_id == prereq_topic.id,
                    UserTopicProgress.theory_completed == True
                ).first()
                if not prog:
                    raise HTTPException(status_code=403, detail=f"Najpierw ukończ: {prereq_slug}")

    # Generate theory if not cached
    if not topic.theory_content:
        prereq_names = []
        for prereq_slug in prereqs:
            prereq_topic = db.query(Topic).filter(Topic.slug == prereq_slug).first()
            if prereq_topic:
                prereq_names.append(prereq_topic.name)

        try:
            content = await generate_theory_lesson(topic.name, topic.slug, topic.difficulty, prereq_names)
            topic.theory_content = json.dumps(content, ensure_ascii=False)
            db.commit()
        except Exception as e:
            logger.error(f"Theory generation failed for {slug}: {e}")
            raise HTTPException(status_code=503, detail="Generowanie lekcji chwilowo niedostępne. Spróbuj ponownie za moment.")

    content = json.loads(topic.theory_content)

    # Generate lab instructions if topic has a lab
    lab_instructions = None
    if topic.lab_type:
        lab_instructions = await generate_lab_instructions(topic.name, topic.slug, topic.lab_type)

    return {
        "topic": {"id": topic.id, "slug": topic.slug, "name": topic.name, "difficulty": topic.difficulty},
        "content": content,
        "lab_instructions": lab_instructions
    }


class QuizSubmitRequest(BaseModel):
    user_id: int
    answers: dict                        # {question_index: "A"}
    response_times: dict = {}            # {question_index: ms} — for confidence detection


@router.post("/{slug}/quiz")
async def submit_quiz(slug: str, req: QuizSubmitRequest, db: Session = Depends(get_db)):
    """Submit quiz answers, get analysis, save errors, award XP."""
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not topic.theory_content:
        raise HTTPException(status_code=400, detail="Theory not loaded yet")

    content = json.loads(topic.theory_content)
    quiz_questions = content.get("quiz", [])

    # Analyze errors (pass response times for confidence detection)
    analysis = await analyze_quiz_errors(
        quiz_questions, req.answers, topic.name, req.response_times
    )
    score = analysis.get("score", 0)

    # Save error items for the Fix Loop
    for error in analysis.get("errors", []):
        item = ErrorItem(
            user_id=user.id,
            topic_slug=slug,
            question=error["question"],
            correct_answer=error["correct_answer"],
            user_answer=error["user_answer"],
            error_type=error.get("error_type", "unknown"),
            explanation=error.get("explanation", "")
        )
        db.add(item)

    # Auto-generate flashcards from theory
    existing_flashcard_fronts = {
        f.front for f in db.query(Flashcard).filter(
            Flashcard.user_id == user.id,
            Flashcard.topic_slug == slug
        ).all()
    }
    for fc_data in content.get("flashcards", []):
        if fc_data["front"] not in existing_flashcard_fronts:
            fc = Flashcard(
                user_id=user.id,
                topic_slug=slug,
                front=fc_data["front"],
                back=fc_data["back"],
                example=fc_data.get("example")
            )
            db.add(fc)

    # Update or create progress
    progress = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user.id,
        UserTopicProgress.topic_id == topic.id
    ).first()

    xp_awarded = 0
    if not progress:
        progress = UserTopicProgress(user_id=user.id, topic_id=topic.id)
        db.add(progress)

    if not progress.theory_completed:
        progress.theory_completed = True
        xp_awarded += XP_THEORY

    if score >= 70 and (progress.quiz_score is None or score > progress.quiz_score):
        xp_awarded += XP_QUIZ_PASS

    progress.quiz_score = max(score, progress.quiz_score or 0)
    user.total_xp = (user.total_xp or 0) + xp_awarded
    progress.xp_awarded = (progress.xp_awarded or 0) + xp_awarded

    db.commit()

    new_achievements = check_and_award_achievements(user, db)

    return {
        "score": score,
        "xp_awarded": xp_awarded,
        "analysis": analysis,
        "new_achievements": new_achievements,
        "level_info": calculate_level_from_xp(user.total_xp)
    }


class LabCompleteRequest(BaseModel):
    user_id: int
    writeup_steps: dict  # {reconnaissance, exploitation, result, lesson}


@router.post("/{slug}/lab/complete")
async def complete_lab(slug: str, req: LabCompleteRequest, db: Session = Depends(get_db)):
    """Mark lab as complete and generate writeup."""
    from backend.models.lab_attempt import LabAttempt
    from backend.services.lesson_service import generate_writeup

    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    writeup_data = await generate_writeup(topic.name, req.writeup_steps, {})

    # Save lab attempt
    attempt = LabAttempt(
        user_id=user.id,
        topic_slug=slug,
        lab_type=topic.lab_type or "manual",
        completed=True,
        flag_captured=True,
        score=100.0,
        writeup=json.dumps(writeup_data, ensure_ascii=False),
        completed_at=datetime.utcnow(),
        xp_awarded=XP_LAB
    )
    db.add(attempt)

    # Update progress
    progress = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user.id,
        UserTopicProgress.topic_id == topic.id
    ).first()
    if not progress:
        progress = UserTopicProgress(user_id=user.id, topic_id=topic.id)
        db.add(progress)

    xp_awarded = 0
    if not progress.lab_completed:
        progress.lab_completed = True
        progress.completed_at = datetime.utcnow()
        xp_awarded = XP_LAB
        user.total_xp = (user.total_xp or 0) + xp_awarded

    db.commit()

    new_achievements = check_and_award_achievements(user, db)

    return {
        "writeup": writeup_data,
        "xp_awarded": xp_awarded,
        "new_achievements": new_achievements,
        "level_info": calculate_level_from_xp(user.total_xp)
    }
