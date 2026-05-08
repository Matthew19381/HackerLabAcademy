"""
Certificate generation: award PDF when user completes all topics in a category.
"""
import logging
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.topic import Topic, UserTopicProgress
from backend.models.user import User
from backend.models.certificate import Certificate
from backend.services.certificate_service import generate_certificate_pdf

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/certificates", tags=["certificates"])


@router.get("/list")
def list_certificates(user_id: int, db: Session = Depends(get_db)):
    """List all certificates issued to user."""
    certs = db.query(Certificate).filter(Certificate.user_id == user_id, Certificate.is_active == True).order_by(Certificate.issued_at.desc()).all()
    return [
        {
            "id": c.id,
            "category": c.category,
            "topic_slugs": json.loads(c.topic_slugs),
            "issued_at": c.issued_at.isoformat(),
            "certificate_code": c.certificate_code,
        }
        for c in certs
    ]


@router.get("/generate")
def generate_certificate(
    category: str = Query(..., description="Category: Fundamentals, OWASP Top 10, Advanced"),
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Generate a certificate PDF if user completed all topics in the category."""
    # Validate category
    valid_categories = {"Fundamentals", "OWASP Top 10", "Advanced"}
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail="Invalid category")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all topics in this category
    topics = db.query(Topic).filter(Topic.category == category).order_by(Topic.order_index).all()
    if not topics:
        raise HTTPException(status_code=404, detail="No topics in this category")

    topic_slugs = [t.slug for t in topics]

    # Check user progress: all topics must have theory_completed and quiz_passed
    for t in topics:
        progress = db.query(UserTopicProgress).filter(
            UserTopicProgress.user_id == user_id,
            UserTopicProgress.topic_id == t.id
        ).first()
        if not progress or not progress.theory_completed or not progress.quiz_passed:
            raise HTTPException(
                status_code=400,
                detail=f"Topic '{t.name}' not completed (theory/quiz required)."
            )

    # Check if certificate already exists and is active
    existing = db.query(Certificate).filter(
        Certificate.user_id == user_id,
        Certificate.category == category,
        Certificate.is_active == True
    ).first()
    if existing:
        # Return existing PDF if file exists, else regenerate
        pdf_path = existing.certificate_code + ".pdf"
        # For simplicity, return existing record info; client can re-request if file missing
        return {
            "already_generated": True,
            "certificate_code": existing.certificate_code,
            "issued_at": existing.issued_at.isoformat(),
        }

    # Generate certificate code: HLA-CATEG-YYYYMMDD-USERID (short)
    date_str = datetime.utcnow().strftime("%Y%m%d")
    code = f"HLA-{category.replace(' ', '').upper()}-{date_str}-{user_id}"

    # Create PDF
    try:
        pdf_path = generate_certificate_pdf(
            user_name=user.name,
            category=category,
            topic_names=[t.name for t in topics],
            certificate_code=code,
            issued_date=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

    # Save certificate record
    cert = Certificate(
        user_id=user_id,
        category=category,
        topic_slugs=json.dumps(topic_slugs),
        certificate_code=code,
        is_active=True,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    return {
        "certificate_code": code,
        "issued_at": cert.issued_at.isoformat(),
        "pdf_path": pdf_path,
        "status": "generated"
    }


@router.get("/download/{certificate_code}")
def download_certificate(certificate_code: str, db: Session = Depends(get_db)):
    """Download the PDF for a given certificate code."""
    cert = db.query(Certificate).filter(Certificate.certificate_code == certificate_code, Certificate.is_active == True).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    pdf_filename = f"{certificate_code}.pdf"
    # Assume pdf stored in exports/certificates/
    # For now, rebuild path from pdf_service output
    # pdf_service should store in backend/exports/certificates/
    path = f"exports/certificates/{pdf_filename}"
    # If file not found, try generate? No, 404.
    import os
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=pdf_filename,
        headers={"Content-Disposition": f'attachment; filename="{pdf_filename}"'},
    )
