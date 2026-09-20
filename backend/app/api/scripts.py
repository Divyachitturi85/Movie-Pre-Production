import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.project import Project
from app.models.script import Script
from app.models.scene import Scene
from app.models.explainability import AIExplainabilityRecord
from app.schemas.script import ScriptResponse, ScriptParseRequest
from app.services.pdf_service import PDFService
from app.services.script_parser import ScriptParser

router = APIRouter(prefix="/projects/{project_id}/script", tags=["Scripts"])

@router.post("/upload", response_model=ScriptResponse)
async def upload_script_pdf(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Security: Validate file extension
    filename = file.filename or "script.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only .pdf screenplay documents are accepted."
        )

    # Save file to disk
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    clean_filename = f"proj_{project_id}_{os.path.basename(filename)}"
    dest_path = os.path.join(settings.UPLOAD_DIR, clean_filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(dest_path)
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        os.remove(dest_path)
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    # Run PDF Ingestion & OCR pipeline
    pdf_service = PDFService(ocr_lang=settings.OCR_LANGUAGE)
    try:
        extract_result = pdf_service.extract_text(dest_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF document: {str(e)}"
        )

    # Remove existing script if present
    existing_script = db.query(Script).filter(Script.project_id == project_id).first()
    if existing_script:
        db.delete(existing_script)
        db.commit()

    script = Script(
        project_id=project_id,
        filename=filename,
        file_path=dest_path,
        file_size_bytes=file_size,
        page_count=extract_result["page_count"],
        extraction_method=extract_result["extraction_method"],
        ocr_confidence=extract_result["ocr_confidence"],
        raw_text=extract_result["raw_text"],
        cleaned_text=extract_result["cleaned_text"]
    )
    db.add(script)

    # Record AI Explainability for PDF / OCR stage
    explain_rec = AIExplainabilityRecord(
        project_id=project_id,
        stage="OCR" if extract_result["extraction_method"] == "PADDLE_OCR" else "PDF_EXTRACTION",
        target_entity=f"Script: {filename}",
        input_data=f"PDF File: {filename} ({file_size} bytes, {extract_result['page_count']} pages)",
        ai_method="PaddleOCR Engine (Scanned PDF Fallback)" if extract_result["extraction_method"] == "PADDLE_OCR" else "PyMuPDF Direct Text Extraction",
        output_detected=f"Extracted {len(extract_result['cleaned_text'])} characters. Quality score: {extract_result['quality_score']:.2f}",
        confidence=extract_result["ocr_confidence"],
        fallback_used=(extract_result["extraction_method"] == "PADDLE_OCR"),
        fallback_reason="Low digital text density detected in PDF pages; switched to high-resolution OCR" if extract_result["extraction_method"] == "PADDLE_OCR" else None,
        details={
            "page_count": extract_result["page_count"],
            "quality_score": extract_result["quality_score"],
            "extraction_method": extract_result["extraction_method"]
        }
    )
    db.add(explain_rec)

    # Run screenplay parser to populate scenes
    parser = ScriptParser()
    parsed_scenes = parser.parse_screenplay(extract_result["cleaned_text"])

    # Clear old scenes
    db.query(Scene).filter(Scene.project_id == project_id).delete()

    for idx, sc_data in enumerate(parsed_scenes):
        scene_model = Scene(
            project_id=project_id,
            scene_number=sc_data.get("scene_number", idx + 1),
            heading=sc_data.get("heading", ""),
            interior_exterior=sc_data.get("interior_exterior", "INT"),
            location_name=sc_data.get("location_name", "UNKNOWN"),
            time_of_day=sc_data.get("time_of_day", "DAY"),
            page_start=idx + 1.0,
            page_end=idx + 1.0 + sc_data.get("estimated_pages", 0.5),
            estimated_pages=sc_data.get("estimated_pages", 0.5),
            estimated_duration_minutes=sc_data.get("estimated_duration_minutes", 60),
            raw_content=sc_data.get("raw_content", ""),
            action_text=sc_data.get("action_text", ""),
            dialogue_count=sc_data.get("dialogue_count", 0),
            complexity_score=1.0,
            complexity_level="LOW",
            sequence_order=idx + 1
        )
        db.add(scene_model)

    project.status = "PARSED"
    project.current_stage = "PARSED"
    db.commit()
    db.refresh(script)

    return script

@router.get("", response_model=ScriptResponse)
def get_script(project_id: int, db: Session = Depends(get_db)):
    script = db.query(Script).filter(Script.project_id == project_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="No script uploaded for this project")
    return script

@router.post("/parse", response_model=ScriptResponse)
def reparse_script(
    project_id: int,
    payload: ScriptParseRequest,
    db: Session = Depends(get_db)
):
    """Re-runs screenplay parser on custom text or stored script"""
    script = db.query(Script).filter(Script.project_id == project_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    text_to_parse = payload.raw_text or script.cleaned_text or script.raw_text
    parser = ScriptParser()
    parsed_scenes = parser.parse_screenplay(text_to_parse)

    db.query(Scene).filter(Scene.project_id == project_id).delete()

    for idx, sc_data in enumerate(parsed_scenes):
        scene_model = Scene(
            project_id=project_id,
            scene_number=sc_data.get("scene_number", idx + 1),
            heading=sc_data.get("heading", ""),
            interior_exterior=sc_data.get("interior_exterior", "INT"),
            location_name=sc_data.get("location_name", "UNKNOWN"),
            time_of_day=sc_data.get("time_of_day", "DAY"),
            page_start=idx + 1.0,
            page_end=idx + 1.0 + sc_data.get("estimated_pages", 0.5),
            estimated_pages=sc_data.get("estimated_pages", 0.5),
            estimated_duration_minutes=sc_data.get("estimated_duration_minutes", 60),
            raw_content=sc_data.get("raw_content", ""),
            action_text=sc_data.get("action_text", ""),
            dialogue_count=sc_data.get("dialogue_count", 0),
            complexity_score=1.0,
            complexity_level="LOW",
            sequence_order=idx + 1
        )
        db.add(scene_model)

    script.cleaned_text = text_to_parse
    db.commit()
    db.refresh(script)
    return script
