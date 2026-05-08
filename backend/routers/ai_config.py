import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-config", tags=["ai-config"])


class AIProviderRequest(BaseModel):
    provider: str  # "gemini", "ollama", "openrouter"


class AIProviderResponse(BaseModel):
    provider: str
    available_providers: list
    models: dict


@router.get("/provider")
def get_ai_provider():
    """Get current AI provider and available options."""
    return {
        "provider": settings.AI_PROVIDER,
        "available_providers": ["gemini", "ollama", "openrouter", "auto"],
        "models": {
            "gemini": "gemini-2.0-flash",
            "ollama": settings.OLLAMA_MODEL,
            "openrouter": settings.OPENROUTER_MODEL or "google/gemini-2.0-flash-001",
        },
        "openrouter_models": [
            "google/gemini-2.0-flash-001",
            "google/gemini-2.5-pro-preview",
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "anthropic/claude-3.5-sonnet",
            "meta-llama/llama-3.3-70b-instruct",
        ]
    }


@router.post("/provider")
def set_ai_provider(req: AIProviderRequest):
    """Set AI provider (runtime change, not persisted to .env)."""
    valid_providers = ["gemini", "ollama", "openrouter", "auto"]
    if req.provider not in valid_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Must be one of: {valid_providers}"
        )

    # Validate that required API keys are present
    if req.provider == "gemini" and not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=400, detail="Gemini API key not configured")
    elif req.provider == "openrouter" and not settings.OPENROUTER_API_KEY:
        raise HTTPException(status_code=400, detail="OpenRouter API key not configured")

    settings.AI_PROVIDER = req.provider
    logger.info(f"AI provider changed to: {req.provider}")

    return {
        "provider": settings.AI_PROVIDER,
        "message": f"AI provider set to {req.provider}"
    }


@router.get("/test")
async def test_ai_connection(provider: str = None):
    """Test AI connection with current or specified provider."""
    from backend.services.ai_service import generate_text
    import time

    test_prompt = "Respond with exactly: 'OK'"
    start = time.time()

    try:
        # Temporarily override provider if testing a specific one
        original = settings.AI_PROVIDER
        if provider:
            settings.AI_PROVIDER = provider

        response = await generate_text(test_prompt)
        elapsed = round(time.time() - start, 2)

        if provider:
            settings.AI_PROVIDER = original

        return {
            "success": True,
            "provider": provider or original,
            "response": response[:100],
            "elapsed_seconds": elapsed
        }
    except Exception as e:
        if provider:
            settings.AI_PROVIDER = original
        return {
            "success": False,
            "provider": provider or settings.AI_PROVIDER,
            "error": str(e),
            "elapsed_seconds": round(time.time() - start, 2)
        }
