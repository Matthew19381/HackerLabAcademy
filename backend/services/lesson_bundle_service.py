"""
Lesson bundle service: create ZIP containing PDF + audio for a lesson.
"""
import os
import tempfile
import zipfile
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Paths
PDF_EXPORTS_DIR = "exports"
AUDIO_DIR = "audio"

def create_lesson_bundle(slug: str, pdf_path: Optional[str] = None, audio_path: Optional[str] = None) -> str:
    """
    Create a ZIP bundle with lesson PDF and audio.

    Args:
        slug: Lesson slug
        pdf_path: Optional explicit PDF path (default: exports/lesson_{slug}.pdf)
        audio_path: Optional explicit audio path (default: audio/lesson_{slug}.mp3)

    Returns:
        Path to created ZIP file
    """
    if pdf_path is None:
        pdf_path = os.path.join(PDF_EXPORTS_DIR, f"lesson_{slug}.pdf")
    if audio_path is None:
        audio_path = os.path.join(AUDIO_DIR, f"lesson_{slug}.mp3")

    # Ensure files exist
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio not found: {audio_path}")

    # Create ZIP in temp dir (or exports)
    zip_filename = f"lesson_{slug}_bundle.zip"
    zip_path = os.path.join(PDF_EXPORTS_DIR, zip_filename)

    # If already exists, reuse (simple caching)
    if os.path.exists(zip_path):
        logger.info(f"Bundle already exists: {zip_path}")
        return zip_path

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(pdf_path, arcname=f"{slug}.pdf")
        zf.write(audio_path, arcname=f"{slug}.mp3")

    logger.info(f"Created bundle: {zip_path}")
    return zip_path
