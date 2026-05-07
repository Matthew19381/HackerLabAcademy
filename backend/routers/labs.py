import logging
from fastapi import APIRouter
from services.lab_service import get_lab_status, start_lab, stop_lab, reset_lab, get_lab_url

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/labs", tags=["labs"])


@router.get("/status")
def lab_status():
    return get_lab_status()


@router.post("/start")
def lab_start():
    return start_lab()


@router.post("/stop")
def lab_stop():
    return stop_lab()


@router.post("/reset")
def lab_reset():
    return reset_lab()


@router.get("/url/{lab_type}")
def lab_url(lab_type: str):
    url = get_lab_url(lab_type)
    return {"url": url, "lab_type": lab_type}
