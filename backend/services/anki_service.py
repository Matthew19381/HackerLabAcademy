"""Anki deck export using genanki."""
import genanki
import hashlib
import logging
import os

logger = logging.getLogger(__name__)
EXPORTS_DIR = "exports"


def _stable_id(seed: str) -> int:
    return int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)


def export_flashcards_to_anki(user_id: int, flashcards: list, deck_name: str = "HackerLabAcademy") -> str:
    """Export flashcards to .apkg file. Returns file path."""
    model = genanki.Model(
        _stable_id(f"hackerlab_model_{deck_name}"),
        "HackerLabAcademy Card",
        fields=[
            {"name": "Front"},
            {"name": "Back"},
            {"name": "Example"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "<div style='font-family:monospace;font-size:16px;'>{{Front}}</div>",
                "afmt": """<div style='font-family:monospace;font-size:16px;'>{{Front}}</div>
<hr>
<div style='font-size:15px;color:#39d353;'>{{Back}}</div>
{{#Example}}<pre style='background:#0d1117;color:#e3b341;padding:8px;border-radius:4px;font-size:12px;'>{{Example}}</pre>{{/Example}}""",
            }
        ],
        css="""
.card { background: #161b22; color: #c9d1d9; font-size: 14px; padding: 20px; }
hr { border-color: #30363d; }
""",
    )

    deck = genanki.Deck(_stable_id(f"hackerlab_deck_{user_id}_{deck_name}"), deck_name)

    for fc in flashcards:
        note = genanki.Note(
            model=model,
            fields=[
                str(fc.get("front", "")),
                str(fc.get("back", "")),
                str(fc.get("example", "") or ""),
            ],
        )
        deck.add_note(note)

    path = os.path.join(EXPORTS_DIR, f"hackerlabacademy_{user_id}.apkg")
    genanki.Package(deck).write_to_file(path)
    logger.info(f"Anki deck exported: {path} ({len(flashcards)} cards)")
    return path
