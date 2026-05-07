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

    # AI Provider selection: "gemini", "ollama", "auto" (gemini → fallback ollama)
    AI_PROVIDER: str = "gemini"

    # Database
    DATABASE_URL: str = "sqlite:///./HackerLabAcademy.db"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
