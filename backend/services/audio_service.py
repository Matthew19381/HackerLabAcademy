"""
Audio generation using edge-tts (Microsoft Neural TTS, free, no API key needed).
Voice: pl-PL-ZofiaNeural (Polish female) — clear and natural.
"""
import asyncio
import hashlib
import logging
import os

import edge_tts

logger = logging.getLogger(__name__)

AUDIO_DIR = "audio"
VOICE = "pl-PL-ZofiaNeural"


def _audio_path(key: str) -> str:
    safe = hashlib.md5(key.encode()).hexdigest()
    return os.path.join(AUDIO_DIR, f"{safe}.mp3")


async def generate_lesson_audio(topic_slug: str, content: dict) -> str:
    """
    Generate MP3 audio summary of a theory lesson.
    Returns relative path to audio file.
    """
    path = _audio_path(f"lesson_{topic_slug}")
    if os.path.exists(path):
        return path

    text = _build_lesson_script(content)
    try:
        communicate = edge_tts.Communicate(text=text, voice=VOICE, rate="+5%")
        await communicate.save(path)
        logger.info(f"Audio generated: {path}")
        return path
    except Exception as e:
        logger.error(f"Audio generation failed for {topic_slug}: {e}")
        raise


def _build_lesson_script(content: dict) -> str:
    """Build spoken script from lesson content."""
    parts = []

    title = content.get("title", "Lekcja")
    parts.append(f"Lekcja: {title}.")
    parts.append("")

    intro = content.get("intro", "")
    if intro:
        parts.append(intro)
        parts.append("")

    for section in content.get("sections", [])[:4]:
        heading = section.get("heading", "")
        text = section.get("content", "")
        if heading and text:
            parts.append(f"{heading}.")
            parts.append(text)
            parts.append("")

    how_attack = content.get("how_attack_works", "")
    if how_attack:
        parts.append("Jak działa ten atak.")
        parts.append(how_attack)
        parts.append("")

    how_defend = content.get("how_to_defend", "")
    if how_defend:
        parts.append("Jak się bronić.")
        parts.append(how_defend)
        parts.append("")

    concepts = content.get("key_concepts", [])[:5]
    if concepts:
        parts.append("Kluczowe pojęcia.")
        for c in concepts:
            parts.append(f"{c.get('term', '')} — {c.get('definition', '')}.")
        parts.append("")

    parts.append("Koniec lekcji. Powodzenia na quizie!")

    return " ".join(parts)


async def generate_flashcard_audio(text: str, card_id: int) -> str:
    """Generate audio for a single flashcard front."""
    path = _audio_path(f"card_{card_id}")
    if os.path.exists(path):
        return path
    try:
        communicate = edge_tts.Communicate(text=text, voice=VOICE)
        await communicate.save(path)
        return path
    except Exception as e:
        logger.error(f"Flashcard audio failed for card {card_id}: {e}")
        raise
