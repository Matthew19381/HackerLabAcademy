from typing import Optional
from pydantic_settings import BaseSettings

# Export directories (relative to working directory /app)
PDF_EXPORT_DIR = "exports"
AUDIO_DIR = "audio"


class Settings(BaseSettings):
    # Gemini (cloud)
    GEMINI_API_KEY: str = None

    # Ollama (local)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # OpenRouter (cloud - multiple models)
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "google/gemini-2.0-flash-001"  # Can use any model supported by OpenRouter

    # AI Provider selection: "gemini", "ollama", "openrouter", "auto" (gemini → fallback openrouter → fallback ollama)
    AI_PROVIDER: str = "gemini"

    # Database
    DATABASE_URL: str = "sqlite:///./HackerLabAcademy.db"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
