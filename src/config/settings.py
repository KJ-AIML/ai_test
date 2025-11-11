from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # OpenAI settings
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL_BASIC: str | None = None
    OPENAI_MODEL_REASONING: str | None = None

    # Google settings
    GOOGLE_API_KEY: str | None = None
    GOOGLE_MODEL_BASIC: str | None = None
    GOOGLE_MODEL_REASONING: str | None = None

    # Environment settings
    DEBUG: bool = False
    SECRET_KEY: str = "your-default-secret-key"

    # Database settings
    DATABASE_URL: str = "sqlite:///db.sqlite3"

    # API settings
    API_PREFIX: str = "/api"

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0

    # Cache settings
    CACHE_TTL: int = 900

    # Logging settings
    LOG_LEVEL: str = "info"
    LOG_SAVE_TO_FILE: bool = False
    LOG_FILE: str = "src/logs/app.log"
    LOG_AUTO_SETUP: bool = True

    # Server Configuration
    SERVER_PORT: int = 3000
    SERVER_HOST: str = "0.0.0.0"

    # RAG settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    VECTOR_STORE_TYPE: str = "qdrant"
    VECTOR_STORE_COLLECTION_NAME: str = "test"
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7

    # Qdrant settings
    QDRANT_URL: str = "https://1aa8836c-98cf-4950-b931-26685f2f20e0.us-west-2-0.aws.cloud.qdrant.io:6333"
    QDRANT_API_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.w1-rBBGDzWWMWMKZ51TMCcatNHc6ZcOmTTKb_K0fPWI"

    # Document processing settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    SUPPORTED_FORMATS: List[str] = ["pdf", "txt", "md", "docx", "csv"]

    # Allowed hosts
    ALLOWED_HOSTS: List[str] = ["*"]

    # Qdrant RAG settings
    QDRANT_URL: str = "https://1aa8836c-98cf-4950-b931-26685f2f20e0.us-west-2-0.aws.cloud.qdrant.io:6333"
    QDRANT_API_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.w1-rBBGDzWWMWMKZ51TMCcatNHc6ZcOmTTKb_K0fPWI"
    QDRANT_COLLECTION_NAME: str = "test"

    class Config:
        env_file = BASE_DIR / ".env"
        case_sensitive = True


settings = Settings()
