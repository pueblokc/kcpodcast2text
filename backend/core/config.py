"""
Application configuration management
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Podcast Transcription Archive"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/podcasts.db"

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_TOKEN: Optional[str] = None
    DEEPGRAM_API_KEY: Optional[str] = None

    # Transcription
    DEFAULT_TRANSCRIPTION_PROVIDER: str = "local"  # local, openai, huggingface, deepgram
    WHISPER_MODEL_SIZE: str = "base"  # tiny, base, small, medium, large
    MAX_FILES_PER_DAY: int = 50
    BATCH_SIZE: int = 5

    # Paths
    MODELS_DIR: Path = Path("./models")
    DATA_DIR: Path = Path("./data")
    TEMP_DIR: Path = Path("./data/temp")
    TRANSCRIPTS_DIR: Path = Path("./data/transcripts")

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # External Integrations
    GOOGLE_DRIVE_CREDENTIALS: Optional[str] = None
    NOTION_API_KEY: Optional[str] = None
    NOTION_DATABASE_ID: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        self.TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
