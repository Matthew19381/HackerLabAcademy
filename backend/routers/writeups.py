import logging
import json
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.writeup_template import WriteupTemplate, Writeup
from models.user import User
from services.pdf_service import generate_pdf_from_markdown

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/writeups", tags=["writeups"])


@router.get("/templates")
def get_writeup_templates(
    category: str = None,
    db: Session = Depends(get_db)
):
    """List active writeup templates, optionally filtered by category."""
    query = db.query(WriteupTemplate).filter(WriteupTemplate.is_active == True)
    if category:
        query = query.filter(WriteupTemplate.category == category)
    templates = query.order_by(WriteupTemplate.name).all()

    return [
        {
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "variables": json.loads(t.variables_json) if t.variables_json else [],
        }
        for t in templates
    ]


class GenerateWriteupRequest(BaseModel):
    user_id: int
    template_id: int
    variables: dict  # e.g. {"vuln": "SQLi", "impact": "..."}
    title: str = None  # optional custom title


@router.post("/generate")
def generate_writeup(
    req: GenerateWriteupRequest,
    db: Session = Depends(get_db)
):
    """Render a writeup from template + variables, save and generate PDF."""
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    template = db.query(WriteupTemplate).filter(WriteupTemplate.id == req.template_id, WriteupTemplate.is_active == True).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Render markdown by replacing {{var}} with values
    try:
        # Uses Python format: {variable}
        # Ensure all required variables present
        content_md = template.template_md.format(**{k: v for k, v in req.variables.items() if v is not None})
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing variable: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Template error: {e}")

    # Title: custom or template name
    title = req.title or template.name

    # Create writeup record
    writeup = Writeup(
        user_id=req.user_id,
        template_id=req.template_id,
        title=title,
        content_md=content_md,
        rendered_pdf_path=None,
    )
    db.add(writeup)
    db.commit()
    db.refresh(writeup)

    # Generate PDF
    try:
        pdf_path = generate_pdf_from_markdown(content_md, title=title)
        writeup.rendered_pdf_path = pdf_path
        db.commit()
    except Exception as e:
        logger.error(f"PDF generation for writeup failed: {e}")
        # Continue without PDF

    return {
        "id": writeup.id,
        "title": writeup.title,
        "pdf_available": bool(writeup.rendered_pdf_path),
        "created_at": writeup.created_at.isoformat(),
    }


@router.get("/history/{user_id}")
def get_writeup_history(user_id: int, db: Session = Depends(get_db)):
    """List all writeups for user."""
    writeups = db.query(Writeup).filter(Writeup.user_id == user_id).order_by(Writeup.created_at.desc()).all()
    return [
        {
            "id": w.id,
            "title": w.title,
            "template_id": w.template_id,
            "template_name": w.template.name if w.template else None,
            "pdf_available": bool(w.rendered_pdf_path),
            "created_at": w.created_at.isoformat(),
        }
        for w in writeups
    ]


@router.get("/download/{writeup_id}")
def download_writeup_pdf(writeup_id: int, db: Session = Depends(get_db)):
    """Download generated PDF for a writeup."""
    writeup = db.query(Writeup).filter(Writeup.id == writeup_id).first()
    if not writeup or not writeup.rendered_pdf_path:
        raise HTTPException(status_code=404, detail="PDF nie jest dostępne")

    if not os.path.exists(writeup.rendered_pdf_path):
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")

    filename = f"writeup_{writeup_id}.pdf"
    return FileResponse(
        path=writeup.rendered_pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def seed_sample_templates(db: Session):
    """Seed sample writeup templates for labs and CTF."""
    templates = [
        {
            "name": "Security Lab Report (DVWA)",
            "category": "lab",
            "variables_json": json.dumps([
                {"name": "vuln", "type": "string", "label": "Nazwa podatności"},
                {"name": "steps", "type": "string", "label": "Kroki ataku (opis)"},
                {"name": "impact", "type": "string", "label": "Wpływ"},
                {"name": "remediation", "type": "string", "label": "Jak naprawić"},
            ]),
            "template_md": """# Raport z Laboratorium: {vuln}

## 1. Opis podatności
{vuln} jest podatnością pozwalająca na...

## 2. Kroki reprodukcji
{steps}

## 3. Wpływ
{impact}

## 4. Zalecenia naprawcze
{remediation}

---

*Wygenerowano przez HackerLabAcademy*""",
        },
        {
            "name": "CTF Write-up",
            "category": "ctf",
            "variables_json": json.dumps([
                {"name": "challenge", "type": "string", "label": "Nazwa challenge'u"},
                {"name": "category", "type": "string", "label": "Kategoria"},
                {"name": "flag", "type": "string", "label": "Flaga"},
                {"name": "solution", "type": "string", "label": "Rozwiązanie (krok po kroku)"},
                {"name": "tools", "type": "string", "label": "Użyte narzędzia"},
            ]),
            "template_md": """# CTF Write-up: {challenge}

## Kategoria: {category}
## Flaga: `{flag}`

## Rozwiązanie
{solution}

## Użyte narzędzia
{tools}

---

*HackerLabAcademy CTF Report*""",
        },
    ]

    added = 0
    for t_data in templates:
        existing = db.query(WriteupTemplate).filter(WriteupTemplate.name == t_data["name"]).first()
        if not existing:
            t = WriteupTemplate(
                name=t_data["name"],
                category=t_data["category"],
                template_md=t_data["template_md"],
                variables_json=t_data["variables_json"],
                is_active=True,
            )
            db.add(t)
            added += 1

    if added:
        db.commit()
        logger.info(f"Seeded {added} writeup templates")
