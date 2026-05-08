import logging
import json
import httpx
from backend.config import settings

logger = logging.getLogger(__name__)

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_DEFAULT_MODEL = "google/gemini-2.0-flash-001"  # Default, can be overridden via config


async def generate_text(prompt: str) -> str:
    """Generate text using OpenRouter API."""
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hackerlab.academy",  # Optional, for openrouter stats
        "X-Title": "HackerLabAcademy",  # Optional
    }

    payload = {
        "model": settings.OPENROUTER_MODEL or _DEFAULT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(_OPENROUTER_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"OpenRouter generate_text error: {e}")
            raise


async def generate_json(prompt: str) -> dict:
    """Generate JSON using OpenRouter API."""
    full_prompt = prompt + "\n\nRespond ONLY with valid JSON, no markdown, no code blocks."

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hackerlab.academy",
        "X-Title": "HackerLabAcademy",
    }

    payload = {
        "model": settings.OPENROUTER_MODEL or _DEFAULT_MODEL,
        "messages": [{"role": "user", "content": full_prompt}],
        "stream": False,
        "response_format": {"type": "json_object"},  # Request JSON mode if supported
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            response = await client.post(_OPENROUTER_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"].strip()

            # Strip markdown fences if model adds them
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
            raise ValueError(f"Invalid JSON response from OpenRouter: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"OpenRouter generate_json error: {e}")
            raise
