"""
Certificate PDF generation using fpdf2.
"""
import logging
import os
from datetime import datetime
from fpdf import FPDF
from config import PDF_EXPORT_DIR

logger = logging.getLogger(__name__)

CERT_DIR = os.path.join(PDF_EXPORT_DIR, "certificates")
os.makedirs(CERT_DIR, exist_ok=True)


def generate_certificate_pdf(user_name: str, category: str, topic_names: list[str], certificate_code: str, issued_date: datetime) -> str:
    """
    Generate a course completion certificate PDF.
    Returns the file path.
    """
    pdf = FPDF(orientation="L", format="A4")  # landscape
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header: decorative border (simple)
    pdf.set_fill_color(230, 230, 250)  # light lavender
    pdf.rect(10, 10, 190, 277, style="D")  # border

    # Title
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(50, 50, 150)
    pdf.cell(0, 30, "HackerLabAcademy", ln=True, align="C")

    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 15, "Certificate of Completion", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, f"This certifies that", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, f"{user_name}", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, f"has successfully completed the", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(200, 50, 50)
    pdf.cell(0, 12, f"{category}", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    # Topics list
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 8, "Included topics:", ln=True, align="C")
    for name in topic_names:
        pdf.cell(0, 6, f"• {name}", ln=True, align="C")

    pdf.ln(15)
    # Signature area
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Certificate Code: {certificate_code}", ln=True, align="C")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"Issued: {issued_date.strftime('%Y-%m-%d')}", ln=True, align="C")

    # Save
    filename = f"{certificate_code}.pdf"
    path = os.path.join(CERT_DIR, filename)
    pdf.output(path)
    logger.info(f"Generated certificate PDF: {path}")
    return path
