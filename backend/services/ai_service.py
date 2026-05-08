"""
AI Service Router — selects provider based on config (Gemini, Ollama, or OpenRouter).
All services should import from here instead of direct gemini_service.
"""
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

# Lazy import providers (only if needed)
_gemini_text = None
_gemini_json = None
_ollama_text = None
_ollama_json = None
_openrouter_text = None
_openrouter_json = None


def _load_gemini():
    global _gemini_text, _gemini_json
    if _gemini_text is None:
        try:
            from backend.services.gemini_service import generate_text as gemini_text, generate_json as gemini_json
            _gemini_text = gemini_text
            _gemini_json = gemini_json
            logger.info("Gemini AI service loaded")
        except Exception as e:
            logger.error(f"Failed to load Gemini service: {e}")
            _gemini_text = _gemini_json = None


def _load_ollama():
    global _ollama_text, _ollama_json
    if _ollama_text is None:
        try:
            from backend.services.ollama_service import generate_text as ollama_text, generate_json as ollama_json
            _ollama_text = ollama_text
            _ollama_json = ollama_json
            logger.info("Ollama AI service loaded")
        except Exception as e:
            logger.error(f"Failed to load Ollama service: {e}")
            _ollama_text = _ollama_json = None


def _load_openrouter():
    global _openrouter_text, _openrouter_json
    if _openrouter_text is None:
        try:
            from backend.services.openrouter_service import generate_text as openrouter_text, generate_json as openrouter_json
            _openrouter_text = openrouter_text
            _openrouter_json = openrouter_json
            logger.info("OpenRouter AI service loaded")
        except Exception as e:
            logger.error(f"Failed to load OpenRouter service: {e}")
            _openrouter_text = _openrouter_json = None


async def generate_text(prompt: str) -> str:
    """Generate text using configured AI provider with optional fallback."""
    provider = settings.AI_PROVIDER

    # Load provider if not already loaded
    if provider in ("gemini", "auto"):
        _load_gemini()
    if provider in ("ollama", "auto"):
        _load_ollama()
    if provider in ("openrouter", "auto"):
        _load_openrouter()

    # Try primary provider
    if provider == "gemini" and _gemini_text:
        try:
            return await _gemini_text(prompt)
        except Exception as e:
            logger.error(f"Gemini generate_text failed: {e}")
            if settings.AI_PROVIDER == "auto":
                # Try OpenRouter, then Ollama
                if _openrouter_text:
                    try:
                        logger.info("Falling back to OpenRouter...")
                        return await _openrouter_text(prompt)
                    except Exception:
                        pass
                if _ollama_text:
                    logger.info("Falling back to Ollama...")
                    return await _ollama_text(prompt)
            raise

    elif provider == "openrouter" and _openrouter_text:
        try:
            return await _openrouter_text(prompt)
        except Exception as e:
            logger.error(f"OpenRouter generate_text failed: {e}")
            if settings.AI_PROVIDER == "auto" and _ollama_text:
                logger.info("Falling back to Ollama...")
                return await _ollama_text(prompt)
            raise

    elif provider == "ollama" and _ollama_text:
        try:
            return await _ollama_text(prompt)
        except Exception as e:
            logger.error(f"Ollama generate_text failed: {e}")
            raise

    elif provider == "auto":
        # Try Gemini first, then OpenRouter, then Ollama
        if _gemini_text:
            try:
                return await _gemini_text(prompt)
            except Exception as e:
                logger.warning(f"Gemini failed: {e}, trying OpenRouter...")
                if _openrouter_text:
                    try:
                        return await _openrouter_text(prompt)
                    except Exception:
                        pass
        if _openrouter_text:
            try:
                return await _openrouter_text(prompt)
            except Exception as e:
                logger.warning(f"OpenRouter failed: {e}, trying Ollama...")
        if _ollama_text:
            return await _ollama_text(prompt)

    raise RuntimeError(
        f"No AI provider available. AI_PROVIDER={settings.AI_PROVIDER}. "
        "Check configuration and ensure at least one provider is working."
    )


async def generate_json(prompt: str) -> dict:
    """Generate JSON using configured AI provider with optional fallback."""
    provider = settings.AI_PROVIDER

    # Load provider if not already loaded
    if provider in ("gemini", "auto"):
        _load_gemini()
    if provider in ("ollama", "auto"):
        _load_ollama()
    if provider in ("openrouter", "auto"):
        _load_openrouter()

    # Try primary provider
    if provider == "gemini" and _gemini_json:
        try:
            return await _gemini_json(prompt)
        except Exception as e:
            logger.error(f"Gemini generate_json failed: {e}")
            if settings.AI_PROVIDER == "auto":
                # Try OpenRouter, then Ollama
                if _openrouter_json:
                    try:
                        logger.info("Falling back to OpenRouter...")
                        return await _openrouter_json(prompt)
                    except Exception:
                        pass
                if _ollama_json:
                    logger.info("Falling back to Ollama...")
                    return await _ollama_json(prompt)
            raise

    elif provider == "openrouter" and _openrouter_json:
        try:
            return await _openrouter_json(prompt)
        except Exception as e:
            logger.error(f"OpenRouter generate_json failed: {e}")
            if settings.AI_PROVIDER == "auto" and _ollama_json:
                logger.info("Falling back to Ollama...")
                return await _ollama_json(prompt)
            raise

    elif provider == "ollama" and _ollama_json:
        try:
            return await _ollama_json(prompt)
        except Exception as e:
            logger.error(f"Ollama generate_json failed: {e}")
            raise

    elif provider == "auto":
        # Try Gemini first, then OpenRouter, then Ollama
        if _gemini_json:
            try:
                return await _gemini_json(prompt)
            except Exception as e:
                logger.warning(f"Gemini JSON failed: {e}, trying OpenRouter...")
                if _openrouter_json:
                    try:
                        return await _openrouter_json(prompt)
                    except Exception:
                        pass
        if _openrouter_json:
            try:
                return await _openrouter_json(prompt)
            except Exception as e:
                logger.warning(f"OpenRouter JSON failed: {e}, trying Ollama...")
        if _ollama_json:
            return await _ollama_json(prompt)

    raise RuntimeError(
        f"No AI provider available for JSON. AI_PROVIDER={settings.AI_PROVIDER}. "
        "Check configuration and ensure at least one provider is working."
    )
