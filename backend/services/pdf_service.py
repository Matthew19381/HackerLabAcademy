"""
PDF generation for theory lessons using fpdf2.
"""
import logging
import os
import hashlib
from fpdf import FPDF

logger = logging.getLogger(__name__)

EXPORTS_DIR = "exports"


def _pdf_path(key: str) -> str:
    safe = hashlib.md5(key.encode()).hexdigest()
    return os.path.join(EXPORTS_DIR, f"{safe}.pdf")


def generate_lesson_pdf(topic_slug: str, content: dict) -> str:
    """Generate PDF of theory lesson. Returns file path."""
    path = _pdf_path(f"lesson_{topic_slug}")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Try to use a Unicode font; fall back to latin-1 safe rendering
    _setup_font(pdf)

    title = _safe(content.get("title", "Lekcja"))
    _heading1(pdf, title)

    intro = _safe(content.get("intro", ""))
    if intro:
        _body(pdf, intro)
        pdf.ln(4)

    # Sections
    for section in content.get("sections", []):
        heading = _safe(section.get("heading", ""))
        body = _safe(section.get("content", ""))
        code = section.get("code_example")

        if heading:
            _heading2(pdf, heading)
        if body:
            _body(pdf, body)
        if code:
            _code_block(pdf, _safe(str(code)))
        pdf.ln(3)

    # How attack works
    attack = _safe(content.get("how_attack_works", ""))
    if attack:
        _heading2(pdf, "Jak dziala ten atak")
        _body(pdf, attack)
        pdf.ln(3)

    # How to defend
    defend = _safe(content.get("how_to_defend", ""))
    if defend:
        _heading2(pdf, "Jak sie bronic")
        _body(pdf, defend)
        pdf.ln(3)

    # Real world example
    example = _safe(content.get("real_world_example", ""))
    if example:
        _heading2(pdf, "Przyklad z zycia")
        _body(pdf, example)
        pdf.ln(3)

    # Key concepts
    concepts = content.get("key_concepts", [])
    if concepts:
        pdf.add_page()
        _heading2(pdf, "Kluczowe pojecia")
        for c in concepts:
            term = _safe(c.get("term", ""))
            defn = _safe(c.get("definition", ""))
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 6, f"{term}:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, defn, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

    # Quiz
    quiz = content.get("quiz", [])
    if quiz:
        pdf.add_page()
        _heading2(pdf, "Quiz")
        for i, q in enumerate(quiz):
            question = _safe(q.get("question", ""))
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 6, f"{i + 1}. {question}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            for opt in q.get("options", []):
                pdf.multi_cell(0, 5, f"   {_safe(opt)}", new_x="LMARGIN", new_y="NEXT")
            correct = _safe(q.get("correct", ""))
            explanation = _safe(q.get("explanation", ""))
            pdf.set_font("Helvetica", "I", 9)
            pdf.multi_cell(0, 5, f"Odpowiedz: {correct}. {explanation}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

    # Flashcards
    flashcards = content.get("flashcards", [])
    if flashcards:
        pdf.add_page()
        _heading2(pdf, "Fiszki")
        for fc in flashcards:
            front = _safe(fc.get("front", ""))
            back = _safe(fc.get("back", ""))
            example = fc.get("example")
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 6, front, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, f"  -> {back}", new_x="LMARGIN", new_y="NEXT")
            if example:
                pdf.set_font("Courier", "", 9)
                pdf.multi_cell(0, 5, f"  {_safe(str(example))}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

    pdf.output(path)
    logger.info(f"PDF generated: {path}")
    return path


def _setup_font(pdf: FPDF):
    pdf.set_font("Helvetica", "", 11)


def _heading1(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11)


def _heading2(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", "B", 13)
    pdf.multi_cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)


def _body(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")


def _code_block(pdf: FPDF, text: str):
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Courier", "", 9)
    pdf.multi_cell(0, 5, text, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)


def _safe(text: str) -> str:
    """Replace Polish characters with ASCII equivalents for fpdf2 latin-1 output."""
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
        'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N',
        'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z',
    }
    for pl, en in replacements.items():
        text = text.replace(pl, en)
    return text


def generate_pdf_from_markdown(markdown: str, title: str = None) -> str:
    """
    Generate a PDF from markdown content using fpdf2.
    Supports headers, lists, bold, italic, code blocks.
    Returns the file path.
    """
    import re
    from datetime import datetime

    # Output path
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"writeup_{timestamp}.pdf"
    path = os.path.join(EXPORTS_DIR, filename)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    _setup_font(pdf)

    # Title
    if title:
        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(0, 8, _safe(title), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    lines = markdown.split('\n')
    in_code_block = False
    code_lines = []

    for line in lines:
        line = line.rstrip('\n')

        # Code block markers
        if line.startswith('```'):
            if in_code_block:
                # End code block
                if code_lines:
                    _code_block(pdf, '\n'.join(code_lines))
                    code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Headers
        if line.startswith('# '):
            pdf.set_font("Helvetica", "B", 14)
            pdf.multi_cell(0, 8, _safe(line[2:]), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            continue
        elif line.startswith('## '):
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(0, 8, _safe(line[3:]), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            continue
        elif line.startswith('### '):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 8, _safe(line[4:]), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            continue

        # Unordered list items (-, *)
        stripped = line.strip()
        if stripped.startswith(('- ', '* ')):
            content = stripped[2:]
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, f"  • {_safe(content)}", new_x="LMARGIN", new_y="NEXT")
            continue

        # Ordered list items (1., 2., etc.)
        if re.match(r'^\d+\.\s+', stripped):
            content = re.sub(r'^\d+\.\s+', '', stripped)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, f"  {_safe(content)}", new_x="LMARGIN", new_y="NEXT")
            continue

        # Empty line
        if not stripped:
            pdf.ln(4)
            continue

        # Regular paragraph - strip inline formatting
        pdf.set_font("Helvetica", "", 11)
        # Remove **bold**
        line_clean = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
        # Remove *italic*
        line_clean = re.sub(r'\*(.*?)\*', r'\1', line_clean)
        # Remove `inline code`
        line_clean = re.sub(r'`(.*?)`', r'\1', line_clean)
        # Remove [link](url) -> just text
        line_clean = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', line_clean)

        if line_clean.strip():
            pdf.multi_cell(0, 6, _safe(line_clean), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

    pdf.output(path)
    logger.info(f"PDF generated from markdown: {path}")
    return path
