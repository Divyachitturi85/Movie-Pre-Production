import sys
import logging

# Guard: Pre-import torch before paddle to prevent OpenMP runtime collision on Windows
try:
    import torch
except Exception:
    pass

# Lightweight server startup

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Ensures all models are registered with Base

from app.api.projects import router as projects_router
from app.api.scripts import router as scripts_router
from app.api.analysis import router as analysis_router
from app.api.schedule import router as schedule_router
from app.api.budget import router as budget_router
from app.api.documents import router as documents_router
from app.api.explainability import router as explainability_router
from app.api.reports import router as reports_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("movie_preprod_backend")

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")
    
    # Auto-seed demo project if database has 0 projects
    try:
        from app.core.database import SessionLocal
        from app.models.project import Project
        from app.services.demo_service import DemoService
        with SessionLocal() as db:
            if db.query(Project).count() == 0:
                logger.info("Database is empty. Auto-seeding Project Aurora demo spec...")
                DemoService().load_demo_project(db)
                logger.info("Project Aurora auto-seeded successfully!")
    except Exception as e:
        logger.warning(f"Could not auto-seed demo project: {e}")
        
    yield
    logger.info("Shutting down backend server.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-stack AI-Powered Movie Pre-Production Planning & Production Management System",
    lifespan=lifespan
)
import importlib.util

# Check optional engine module presence without heavy pipeline allocations
_PADDLEOCR_AVAILABLE = importlib.util.find_spec("paddleocr") is not None
_TRANSFORMERS_AVAILABLE = importlib.util.find_spec("transformers") is not None

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://movie-preproduction70mm.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"^(https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?|https:\/\/movie-preproduction70mm(-[a-z0-9-]+)?\.vercel\.app)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler to prevent crashes
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"An internal production system error occurred: {str(exc)}"}
    )

# Health check & Root endpoints
@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_engines": {
            "paddleocr": "ENABLED" if _PADDLEOCR_AVAILABLE else "UNAVAILABLE (Lightweight profile; PyMuPDF direct text active)",
            "ocr": "PaddleOCR" if _PADDLEOCR_AVAILABLE else "PyMuPDF Direct Text (Lightweight Cloud Profile)",
            "spacy": settings.SPACY_MODEL,
            "transformers": settings.HF_MODEL_NAME if _TRANSFORMERS_AVAILABLE else "UNAVAILABLE (spaCy linguistic & rule-based NER active)",
            "ortools": "CP-SAT"
        }
    }

# Include API Routers with standard /api prefix
app.include_router(projects_router, prefix=settings.API_PREFIX)
app.include_router(scripts_router, prefix=settings.API_PREFIX)
app.include_router(analysis_router, prefix=settings.API_PREFIX)
app.include_router(schedule_router, prefix=settings.API_PREFIX)
app.include_router(budget_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(explainability_router, prefix=settings.API_PREFIX)
app.include_router(reports_router, prefix=settings.API_PREFIX)

# Also mount at root as fallback so neither /api/projects nor /projects can ever 404
app.include_router(projects_router, prefix="")
app.include_router(scripts_router, prefix="")
app.include_router(analysis_router, prefix="")
app.include_router(schedule_router, prefix="")
app.include_router(budget_router, prefix="")
app.include_router(documents_router, prefix="")
app.include_router(explainability_router, prefix="")
app.include_router(reports_router, prefix="")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
