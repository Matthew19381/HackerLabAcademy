import json
import logging
from google import genai
from config import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"


async def generate_text(prompt: str) -> str:
    try:
        response = await client.aio.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise


async def generate_json(prompt: str) -> dict:
    full_prompt = prompt + "\n\nRespond ONLY with valid JSON, no markdown, no code blocks."
    try:
        response = await client.aio.models.generate_content(model=MODEL, contents=full_prompt)
        text = response.text.strip()

        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) >= 2:
                text = parts[1]
                if text.startswith("json"):
                    text = text[4:]
                elif text.startswith("JSON"):
                    text = text[4:]

        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()

        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}. Raw response: {text[:500]}")
        raise ValueError(f"Invalid JSON response from Gemini: {e}")
    except Exception as e:
        logger.error(f"Error generating JSON: {e}")
        raise
