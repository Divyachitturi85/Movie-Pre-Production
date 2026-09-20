import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Movie Pre-Production Planning & Production Management System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
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
    
    # Security
    SECRET_KEY: str = "supersecretkeyforlocalmoviepreprod2026"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXPORTS_DIR, exist_ok=True)
