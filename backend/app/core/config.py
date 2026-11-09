import os
import json
from typing import List, Union, Any
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

INSECURE_DEV_SECRET = "dev-insecure-secret-key-change-in-production"
LEGACY_INSECURE_SECRET = "supersecretkeyforlocalmoviepreprod2026"
VERCEL_PRODUCTION_ORIGIN = "https://movie-preproduction70mm.vercel.app"

LOCAL_DEV_ORIGINS = [
    VERCEL_PRODUCTION_ORIGIN,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

def is_production_environment() -> bool:
    env = os.getenv("ENVIRONMENT", "development").strip().lower()
    return env == "production" or bool(os.getenv("RENDER"))

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Movie Pre-Production Planning & Production Management System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./movie_preproduction.db"

    # AI & NLP
    HF_MODEL_NAME: str = "dslim/bert-base-NER"
    SPACY_MODEL: str = "en_core_web_sm"
    OCR_LANGUAGE: str = "en"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    EXPORTS_DIR: str = "./exports"
    MAX_UPLOAD_SIZE_MB: int = 50

    # Security: In production, SECRET_KEY must be provided through environment variables.
    SECRET_KEY: str = Field(default="")

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = Field(
        default_factory=lambda: [VERCEL_PRODUCTION_ORIGIN] if is_production_environment() else LOCAL_DEV_ORIGINS
    )
    FRONTEND_URL: str = ""

    # Table initialization & Demo seeding controls
    AUTO_SEED_DEMO: bool = False

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: Any) -> str:
        prod = is_production_environment()
        val_str = str(v).strip() if v is not None else ""

        if prod:
            if not val_str or val_str in (INSECURE_DEV_SECRET, LEGACY_INSECURE_SECRET):
                raise ValueError(
                    "CRITICAL CONFIGURATION ERROR: SECRET_KEY environment variable is required in "
                    "production but was not set or used an insecure default. "
                    "Please configure a secure SECRET_KEY in your Render environment variables."
                )
            return val_str

        # In development / testing: allow fallback key
        if not val_str:
            return INSECURE_DEV_SECRET
        return val_str

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        if v is None:
            return [VERCEL_PRODUCTION_ORIGIN] if is_production_environment() else list(LOCAL_DEV_ORIGINS)

        parsed: List[str] = []
        if isinstance(v, str):
            clean_str = v.strip()
            if clean_str.startswith("[") and clean_str.endswith("]"):
                try:
                    loaded = json.loads(clean_str)
                    if isinstance(loaded, list):
                        parsed = [str(item).strip().rstrip("/") for item in loaded if str(item).strip()]
                except Exception:
                    pass
            if not parsed and clean_str:
                parsed = [item.strip().rstrip("/") for item in clean_str.split(",") if item.strip()]
        elif isinstance(v, (list, tuple, set)):
            parsed = [str(item).strip().rstrip("/") for item in v if str(item).strip()]

        if not parsed:
            parsed = [VERCEL_PRODUCTION_ORIGIN] if is_production_environment() else list(LOCAL_DEV_ORIGINS)

        return parsed

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXPORTS_DIR, exist_ok=True)
