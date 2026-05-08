import logging
import httpx
from backend.config import settings

logger = logging.getLogger(__name__)

_OLLAMA_URL = f"{settings.OLLAMA_BASE_URL}/chat/completions"
_MODEL = settings.OLLAMA_MODEL


async def generate_text(prompt: str) -> str:
    payload = {
        "model": _MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(_OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise


async def generate_json(prompt: str) -> dict:
    full_prompt = prompt + "\n\nRespond ONLY with valid JSON, no markdown, no code blocks."
    payload = {
        "model": _MODEL,
        "messages": [{"role": "user", "content": full_prompt}],
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            response = await client.post(_OLLAMA_URL, json=payload)
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
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            import json
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}. Raw response: {text[:500]}")
            raise ValueError(f"Invalid JSON response from Ollama: {e}")
        except Exception as e:
            logger.error(f"Error generating JSON via Ollama: {e}")
            raise
