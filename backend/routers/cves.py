import logging
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database import get_db
from backend.models.cve import Cve
from backend.models.flashcard import Flashcard
from backend.services.ai_service import generate_json
from backend.services.cve_service import refresh_cves, fetch_nvd_cves

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cves", tags=["cves"])


class CveRefreshResponse(BaseModel):
    status: str
    fetched: int = None
    transformed: int = None
    added: int = None
    timestamp: str = None
    error: str = None


@router.get("/")
def get_cves(
    topic_slug: str = None,
    severity: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List CVEs, optionally filtered by topic or severity."""
    query = db.query(Cve).filter(Cve.is_active == True)

    if topic_slug:
        query = query.filter(Cve.topic_slug == topic_slug)
    if severity:
        query = query.filter(Cve.severity == severity.upper())

    cves = query.order_by(Cve.published_date.desc()).limit(limit).all()

    return [
        {
            "id": c.id,
            "cve_id": c.cve_id,
            "title": c.title,
            "description": c.description,
            "severity": c.severity,
            "published_date": c.published_date.isoformat(),
            "affected_products": json.loads(c.affected_products) if c.affected_products else [],
            "references": json.loads(c.references) if c.references else [],
            "topic_slug": c.topic_slug,
        }
        for c in cves
    ]


@router.get("/{cve_id}")
def get_cve(cve_id: str, db: Session = Depends(get_db)):
    """Get details of a specific CVE."""
    cve = db.query(Cve).filter(Cve.cve_id == cve_id, Cve.is_active == True).first()
    if not cve:
        raise HTTPException(status_code=404, detail="CVE not found")

    return {
        "id": cve.id,
        "cve_id": cve.cve_id,
        "title": cve.title,
        "description": cve.description,
        "severity": cve.severity,
        "published_date": cve.published_date.isoformat(),
        "affected_products": json.loads(cve.affected_products) if cve.affected_products else [],
        "references": json.loads(cve.references) if cve.references else [],
        "topic_slug": cve.topic_slug,
    }


@router.post("/refresh", response_model=CveRefreshResponse)
def refresh_cves_endpoint(
    days_back: int = 7,
    db: Session = Depends(get_db)
):
    """
    Manually trigger CVE fetch from NVD API.
    Fetches CVEs published in the last N days and adds new ones to database.
    """
    try:
        result = refresh_cves(days_back=days_back)
        return CveRefreshResponse(**result)
    except Exception as e:
        logger.error(f"CVE refresh endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta")
def get_cves_meta(db: Session = Depends(get_db)):
    """Get metadata about CVE database: total count, last updated."""
    total = db.query(Cve).filter(Cve.is_active == True).count()
    latest = db.query(Cve).filter(Cve.is_active == True).order_by(Cve.created_at.desc()).first()
    last_updated = latest.created_at.isoformat() if latest else None

    return {
        "total_cves": total,
        "last_updated": last_updated
    }


class FlashcardFromCveRequest(BaseModel):
    user_id: int
    custom_term: str = None  # optional custom term override


@router.post("/{cve_id}/flashcard")
def create_flashcard_from_cve(
    cve_id: str,
    req: FlashcardFromCveRequest,
    db: Session = Depends(get_db)
):
    """Create a flashcard from a CVE entry (term = CVE ID + title, def = description, example = affected product)."""
    cve = db.query(Cve).filter(Cve.cve_id == cve_id, Cve.is_active == True).first()
    if not cve:
        raise HTTPException(status_code=404, detail="CVE not found")

    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Build front (term) and back (definition)
    term = req.custom_term if req.custom_term else f"{cve.cve_id}: {cve.title}"
    definition = cve.description
    example = None
    if cve.affected_products:
        products = json.loads(cve.affected_products) if isinstance(cve.affected_products, str) else cve.affected_products
        example = f"Dotknięte produkty: {', '.join(products[:3])}"

    # Check if flashcard with same front already exists for this user
    existing = db.query(Flashcard).filter(
        Flashcard.user_id == req.user_id,
        Flashcard.front == term,
        Flashcard.is_active == True
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Fiszka z tym terminem już istnieje")

    card = Flashcard(
        user_id=req.user_id,
        front=term,
        back=definition,
        example=example,
        ease_factor=2.5,
        interval_days=1,
        repetitions=0,
        next_review_date=datetime.utcnow(),
        is_active=True,
    )
    db.add(card)
    db.commit()
    db.refresh(card)

    return {
        "id": card.id,
        "front": card.front,
        "back": card.back,
        "example": card.example,
        "next_review_date": card.next_review_date.isoformat(),
    }


def seed_sample_cves(db: Session):
    """Seed database with sample CVEs for demonstration."""
    samples = [
        {
            "cve_id": "CVE-2021-44228",
            "title": "Log4Shell (Log4j RCE)",
            "description": "Podatność umożliwiająca zdalne wykonanie kodu (RCE) w bibliotece Log4j przez atak JNDI lookup. Przeciwnik może wykonać dowolny kod na serwerze poprzez specjalnie sformatowane komunikaty logowania.",
            "severity": "CRITICAL",
            "published_date": datetime(2021, 12, 9),
            "affected_products": ["Apache Log4j 2.0 - 2.14.1"],
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2021-44228"],
            "topic_slug": "java-security"
        },
        {
            "cve_id": "CVE-2021-42013",
            "title": "Apache HTTP Server Path Traversal & RCE",
            "description": "Podatność w Apache HTTP Server 2.4.50 pozwala na path traversal i potencjalne RCE poprzez specjalnie sformatowane ścieżki URL. Atak może odczytać pliki spoza docelowego katalogu.",
            "severity": "HIGH",
            "published_date": datetime(2021, 10, 5),
            "affected_products": ["Apache HTTP Server 2.4.50", "2.4.51"],
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2021-42013"],
            "topic_slug": "file-inclusion"
        },
        {
            "cve_id": "CVE-2021-3156",
            "title": "Baron Samedit (sudo heap overflow)",
            "description": "Podatność typu heap overflow w sudo pozwala atakującemu z lokalnym dostępem na podniesienie uprawnień do roota poprzez specjalnie sformatowane hasło sudo.",
            "severity": "HIGH",
            "published_date": datetime(2021, 1, 26),
            "affected_products": ["sudo przed 1.9.5p2"],
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2021-3156"],
            "topic_slug": "command-injection"
        },
        {
            "cve_id": "CVE-2020-1472",
            "title": "ZeroLogon (Netlogon Elevation)",
            "description": "Podatność w protokole Netlogon pozwala atakującemu na podniesienie uprawnień domenowych do Administratora Domeny poprzez zafałszowanie komunikacji Netlogon.",
            "severity": "CRITICAL",
            "published_date": datetime(2020, 8, 11),
            "affected_products": ["Windows Server 2008 R2 - 2019"],
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2020-1472"],
            "topic_slug": "auth-bypass"
        },
    ]

    # Add more CVEs
    samples.extend([
        {
            "cve_id": "CVE-2023-38831",
            "title": "Linux Kernel ksmbd RCE",
            "description": "Podatność w podsystemie ksmbd jądra Linux pozwala na zdalne wykonanie kodu poprzez specjalnie spreparowany pakiet SMB.",
            "severity": "HIGH",
            "published_date": datetime(2023, 8, 15),
            "affected_products": ["Linux Kernel przed 6.1.36", "6.4.x przed 6.4.1"],
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-38831"],
            "topic_slug": "command-injection"
        },
        {
            "cve_id": "CVE-2022-22965",
            "title": "Spring Cloud Gateway Code Injection",
            "description": "Podatność w Spring Cloud Gateway pozwala na wstrzyknięcie kodu (SpEL) i zdalne wykonanie kodu poprzez specjalnie spreparowane żądanie.",
            "severity": "CRITICAL",
            "published_date": datetime(2022, 3, 31),
            "affected_products": ["Spring Cloud Gateway 3.1.x przed 3.1.1", "3.0.x przed 3.0.7"],
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2022-22965"],
            "topic_slug": "java-security"
        },
        {
            "cve_id": "CVE-2021-34527",
            "title": "PrintNightmare (Windows Print Spooler)",
            "description": "Podatność w Print Spooler pozwala na podniesienie uprawnień do SYSTEM poprzez dodanie drukarki punktowej i wykonanie złośliwego kodu.",
            "severity": "CRITICAL",
            "published_date": datetime(2021, 7, 1),
            "affected_products": ["Windows 7 - 10", "Windows Server 2008 - 2019"],
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2021-34527"],
            "topic_slug": "privilege-escalation"
        },
        {
            "cve_id": "CVE-2023-2176",
            "title": "Atlassian Confluence RCE",
            "description": "Podatność w Atlassian Confluence Server i Data Center pozwala na zdalne wykonanie kodu poprzez OGNL injection w klasie Action.",
            "severity": "CRITICAL",
            "published_date": datetime(2023, 4, 20),
            "affected_products": ["Confluence Server/Data Center przed 7.13.6", "7.14.x przed 7.14.2"],
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2023-2176"],
            "topic_slug": "java-security"
        },
        {
            "cve_id": "CVE-2022-30190",
            "title": "Follina (MSDT RCE via Office)",
            "description": "Podatność w Microsoft Support Diagnostic Tool (MSDT) pozwala na zdalne wykonanie kodu poprzez specjalnie spreparowany dokument Word używający protokołu URI ms-msdt.",
            "severity": "CRITICAL",
            "published_date": datetime(2022, 5, 27),
            "affected_products": ["Microsoft Office 2013 - 2021", "Windows 7 - 11"],
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2022-30190"],
            "topic_slug": "xss"
        },
    ])

    added = 0
    for cve_data in samples:
        existing = db.query(Cve).filter(Cve.cve_id == cve_data["cve_id"]).first()
        if not existing:
            cve = Cve(
                cve_id=cve_data["cve_id"],
                title=cve_data["title"],
                description=cve_data["description"],
                severity=cve_data["severity"],
                published_date=cve_data["published_date"],
                affected_products=json.dumps(cve_data["affected_products"]),
                references=json.dumps(cve_data["references"]),
                topic_slug=cve_data["topic_slug"],
                is_active=True,
            )
            db.add(cve)
            added += 1
    if added:
        db.commit()
        logger.info(f"Seeded {added} sample CVEs")
