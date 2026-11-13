import os
import shutil
import logging
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

logger = logging.getLogger(__name__)

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
    method = extract_result["extraction_method"]
    char_count = len(extract_result.get("cleaned_text") or "")
    warnings = extract_result.get("warnings", [])

    if method == "PDF_DIRECT":
        stage = "PDF_EXTRACTION"
        ai_method_desc = "PyMuPDF Direct Text Extraction"
        fallback_used = False
        fallback_reason = None
        output_detected = f"Extracted {char_count} characters across {extract_result['page_count']} pages (native digital text layer)."
    elif method == "OCR_COMPLETE":
        stage = "OCR"
        ai_method_desc = "PaddleOCR Optical Character Recognition (Complete)"
        fallback_used = True
        fallback_reason = "Scanned raster pages detected; optical character recognition executed on all pages."
        output_detected = f"Recognized {char_count} characters via PaddleOCR. Mean confidence: {extract_result['ocr_confidence']:.1%}."
    elif method == "OCR_PARTIAL":
        stage = "OCR"
        ai_method_desc = "PaddleOCR Optical Character Recognition (Partial)"
        fallback_used = True
        fallback_reason = "Mixed document: optical recognition succeeded on some pages, but others lacked legible text or failed."
        output_detected = f"Partially recognized {char_count} characters. Mean recognized confidence: {extract_result['ocr_confidence']:.1%}."
    elif method == "OCR_UNAVAILABLE":
        stage = "PDF_EXTRACTION"
        ai_method_desc = "Direct Text Extraction (OCR Engine Unavailable)"
        fallback_used = True
        fallback_reason = "Scanned raster pages detected, but PaddleOCR is not installed in this deployment tier."
        if char_count > 0:
            output_detected = f"Extracted {char_count} characters from existing text layers. Scanned raster pages yielded no text."
        else:
            output_detected = "No text extracted. Document contains scanned raster pages, but optical recognition engine is unavailable."
    elif method == "OCR_FAILED":
        stage = "OCR"
        ai_method_desc = "PaddleOCR Optical Recognition (Attempted - Failed)"
        fallback_used = True
        fallback_reason = "Optical recognition attempted on scanned pages but failed to recognize legible text."
        if char_count > 0:
            output_detected = f"Extracted {char_count} characters. OCR could not recognize text on scanned pages."
        else:
            output_detected = "No text recognized. Optical recognition failed to detect legible text on scanned pages."
    else:
        stage = "PDF_EXTRACTION"
        ai_method_desc = f"PDF Ingestion ({method})"
        fallback_used = False
        fallback_reason = None
        output_detected = f"Extracted {char_count} characters."

    explain_rec = AIExplainabilityRecord(
        project_id=project_id,
        stage=stage,
        target_entity=f"Script: {filename}",
        input_data=f"PDF File: {filename} ({file_size} bytes, {extract_result['page_count']} pages)",
        ai_method=ai_method_desc,
        output_detected=output_detected,
        confidence=extract_result["ocr_confidence"],
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        details={
            "page_count": extract_result["page_count"],
            "quality_score": extract_result["quality_score"],
            "extraction_method": method,
            "warnings": warnings,
            "page_details": extract_result.get("page_details", [])
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

    # Automatically execute AI NLP Breakdown Pipeline & Equipment Extraction
    from app.api.analysis import run_nlp_analysis
    try:
        run_nlp_analysis(project_id, db)
    except Exception as e:
        logger.warning(f"Auto-analysis during upload failed: {e}")

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
    script = db.query(Script).filter(Script.project_id == project_id).first()
    text_to_parse = payload.raw_text or (script.cleaned_text if script else "") or (script.raw_text if script else "")
    if not text_to_parse.strip():
        raise HTTPException(status_code=400, detail="No screenplay text provided to parse")

    if not script:
        script = Script(
            project_id=project_id,
            filename="Pasted_Screenplay.txt",
            file_path="memory://pasted",
            file_size_bytes=len(text_to_parse.encode("utf-8")),
            page_count=max(1, len(text_to_parse.splitlines()) // 54),
            extraction_method="DIRECT_INPUT",
            ocr_confidence=1.0,
            raw_text=text_to_parse,
            cleaned_text=text_to_parse
        )
        db.add(script)
        db.commit()
        db.refresh(script)
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

    # Automatically execute AI NLP Breakdown Pipeline & Equipment Extraction
    from app.api.analysis import run_nlp_analysis
    try:
        run_nlp_analysis(project_id, db)
    except Exception as e:
        logger.warning(f"Auto-analysis during parse failed: {e}")

    return script
