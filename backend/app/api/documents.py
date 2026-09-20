import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
import io
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.scene import Scene
from app.models.character import Character
from app.models.location import Location
from app.models.production_element import ProductionElement
from app.models.schedule import Schedule
from app.models.budget import Budget
from app.models.call_sheet import CallSheet
from app.models.callback_letter import CallbackLetter
from app.schemas.call_sheet import CallSheetResponse, CallSheetUpdate
from app.schemas.callback_letter import CallbackLetterResponse, CallbackLetterCreate
from app.services.call_sheet_service import CallSheetService
from app.services.callback_service import CallbackService
from app.services.document_service import DocumentService

router = APIRouter(prefix="/projects/{project_id}", tags=["Documents & Exports"])

# -------------------------------------------------------------
# Call Sheets Endpoints
# -------------------------------------------------------------
@router.post("/call-sheets/generate", response_model=List[CallSheetResponse])
def generate_call_sheets(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    schedule = db.query(Schedule).filter(Schedule.project_id == project_id).first()
    if not schedule or not schedule.shooting_days:
        raise HTTPException(status_code=400, detail="Please optimize the schedule before generating call sheets.")

    characters = db.query(Character).filter(Character.project_id == project_id).all()
    elements = db.query(ProductionElement).filter(ProductionElement.project_id == project_id).all()

    cs_svc = CallSheetService()
    db.query(CallSheet).filter(CallSheet.project_id == project_id).delete()

    created_sheets = []
    char_dicts = [{"name": c.name} for c in characters]
    elem_dicts = [{"name": e.name, "category": e.category} for e in elements]

    for shoot_day in schedule.shooting_days:
        scenes_data = [
            {
                "scene_number": s.scene.scene_number if s.scene else 1,
                "heading": s.scene.heading if s.scene else "",
                "interior_exterior": s.scene.interior_exterior if s.scene else "INT",
                "time_of_day": s.scene.time_of_day if s.scene else "DAY",
                "pages": s.scene.estimated_pages if s.scene else 0.5,
                "location_name": s.location_name,
                "estimated_start_time": s.estimated_start_time,
                "estimated_duration_minutes": s.estimated_duration_minutes,
                "complexity_level": s.scene.complexity_level if s.scene else "LOW"
            }
            for s in shoot_day.scheduled_scenes
        ]

        d_dict = {
            "day_number": shoot_day.day_number,
            "shoot_date": shoot_day.shoot_date,
            "call_time": shoot_day.call_time,
            "primary_location": shoot_day.primary_location,
            "cast_ids": shoot_day.cast_ids or [],
            "scheduled_scenes": scenes_data
        }

        cs_data = cs_svc.generate_call_sheet_for_day(
            project_name=project.name,
            shooting_day=d_dict,
            characters=char_dicts,
            elements=elem_dicts
        )

        call_sheet = CallSheet(
            project_id=project.id,
            shooting_day_id=shoot_day.id,
            day_number=cs_data["day_number"],
            shoot_date=cs_data["shoot_date"],
            general_call_time=cs_data["general_call_time"],
            location_name=cs_data["location_name"],
            location_address=cs_data["location_address"],
            parking_info=cs_data["parking_info"],
            weather_placeholder=cs_data["weather_placeholder"],
            nearest_hospital=cs_data["nearest_hospital"],
            scenes_summary=cs_data["scenes_summary"],
            cast_calls=cs_data["cast_calls"],
            crew_calls=cs_data["crew_calls"],
            equipment_notes=cs_data["equipment_notes"],
            props_costumes_notes=cs_data["props_costumes_notes"],
            special_instructions=cs_data["special_instructions"],
            meal_break=cs_data["meal_break"],
            emergency_contact=cs_data["emergency_contact"]
        )
        db.add(call_sheet)
        created_sheets.append(call_sheet)

    db.commit()
    return created_sheets

@router.get("/call-sheets", response_model=List[CallSheetResponse])
def list_call_sheets(project_id: int, db: Session = Depends(get_db)):
    sheets = db.query(CallSheet).filter(CallSheet.project_id == project_id).order_by(CallSheet.day_number).all()
    if not sheets:
        # Auto-generate if schedule exists
        schedule = db.query(Schedule).filter(Schedule.project_id == project_id).first()
        if schedule and schedule.shooting_days:
            return generate_call_sheets(project_id, db)
    return sheets

@router.get("/call-sheets/{call_sheet_id}/export/{fmt}")
def export_call_sheet(project_id: int, call_sheet_id: int, fmt: str, db: Session = Depends(get_db)):
    cs = db.query(CallSheet).filter(CallSheet.project_id == project_id, CallSheet.id == call_sheet_id).first()
    if not cs:
        raise HTTPException(status_code=404, detail="Call sheet not found")

    doc_svc = DocumentService()
    cs_dict = {
        "project_name": cs.project.name if cs.project else "Film Production",
        "day_number": cs.day_number,
        "shoot_date": cs.shoot_date,
        "general_call_time": cs.general_call_time,
        "location_name": cs.location_name,
        "location_address": cs.location_address,
        "parking_info": cs.parking_info,
        "weather_placeholder": cs.weather_placeholder,
        "nearest_hospital": cs.nearest_hospital,
        "scenes_summary": cs.scenes_summary or [],
        "cast_calls": cs.cast_calls or [],
        "crew_calls": cs.crew_calls or [],
        "special_instructions": cs.special_instructions,
        "meal_break": cs.meal_break,
        "emergency_contact": cs.emergency_contact
    }

    if fmt.lower() == "pdf":
        pdf_bytes = doc_svc.generate_call_sheets_pdf([cs_dict])
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=CallSheet_Day_{cs.day_number}.pdf"}
        )
    elif fmt.lower() == "docx":
        docx_bytes = doc_svc.generate_call_sheet_docx(cs_dict)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=CallSheet_Day_{cs.day_number}.docx"}
        )
    else:
        return cs_dict

# -------------------------------------------------------------
# Callback Letters Endpoints
# -------------------------------------------------------------
@router.post("/callbacks/generate", response_model=List[CallbackLetterResponse])
def generate_callback_letters(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Generates audition callback letters for all identified characters in the production.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    characters = db.query(Character).filter(Character.project_id == project_id).all()
    if not characters:
        raise HTTPException(status_code=400, detail="No characters found. Run script analysis first.")

    callback_svc = CallbackService()
    db.query(CallbackLetter).filter(CallbackLetter.project_id == project_id).delete()

    char_list = [{"id": c.id, "name": c.name, "role": c.role} for c in characters]
    letter_dicts = callback_svc.generate_bulk_letters(
        project_name=project.name,
        director=project.director,
        characters=char_list
    )

    created_letters = []
    for l_data in letter_dicts:
        cb = CallbackLetter(
            project_id=project.id,
            character_id=l_data.get("character_id"),
            actor_name=l_data["actor_name"],
            actor_email=l_data.get("actor_email"),
            character_name=l_data["character_name"],
            role_type=l_data["role_type"],
            callback_date=l_data["callback_date"],
            callback_time=l_data["callback_time"],
            location=l_data["location"],
            sides_reference=l_data["sides_reference"],
            what_to_prepare=l_data["what_to_prepare"],
            contact_person=l_data["contact_person"],
            contact_email=l_data["contact_email"],
            contact_phone=l_data["contact_phone"],
            special_instructions=l_data.get("special_instructions"),
            letter_body=l_data["letter_body"],
            status="GENERATED"
        )
        db.add(cb)
        created_letters.append(cb)

    db.commit()
    return created_letters

@router.post("/callbacks/single", response_model=CallbackLetterResponse)
def create_single_callback(
    project_id: int,
    payload: CallbackLetterCreate,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    callback_svc = CallbackService()
    letter_dict = callback_svc.generate_letter(
        project_name=project.name,
        director=project.director,
        actor_name=payload.actor_name,
        character_name=payload.character_name,
        role_type=payload.role_type or "LEAD",
        callback_date=payload.callback_date or "Next Monday",
        callback_time=payload.callback_time or "10:00 AM EST",
        location=payload.location or "Studio 3B",
        sides_reference=payload.sides_reference or "Attached Sides",
        what_to_prepare=payload.what_to_prepare,
        contact_person=payload.contact_person or "Sarah Jenkins",
        contact_email=payload.contact_email or "casting@production.com",
        contact_phone=payload.contact_phone or "+1 (555) 012-3456",
        special_instructions=payload.special_instructions,
        actor_email=payload.actor_email,
        character_id=payload.character_id
    )

    cb = CallbackLetter(
        project_id=project_id,
        character_id=payload.character_id,
        actor_name=letter_dict["actor_name"],
        actor_email=letter_dict["actor_email"],
        character_name=letter_dict["character_name"],
        role_type=letter_dict["role_type"],
        callback_date=letter_dict["callback_date"],
        callback_time=letter_dict["callback_time"],
        location=letter_dict["location"],
        sides_reference=letter_dict["sides_reference"],
        what_to_prepare=letter_dict["what_to_prepare"],
        contact_person=letter_dict["contact_person"],
        contact_email=letter_dict["contact_email"],
        contact_phone=letter_dict["contact_phone"],
        special_instructions=letter_dict["special_instructions"],
        letter_body=letter_dict["letter_body"],
        status="GENERATED"
    )
    db.add(cb)
    db.commit()
    db.refresh(cb)
    return cb

@router.get("/callbacks", response_model=List[CallbackLetterResponse])
def list_callback_letters(project_id: int, db: Session = Depends(get_db)):
    letters = db.query(CallbackLetter).filter(CallbackLetter.project_id == project_id).all()
    if not letters:
        characters = db.query(Character).filter(Character.project_id == project_id).all()
        if characters:
            return generate_callback_letters(project_id, db)
    return letters

@router.get("/callbacks/export/pdf")
def export_all_callbacks_pdf(project_id: int, db: Session = Depends(get_db)):
    letters = db.query(CallbackLetter).filter(CallbackLetter.project_id == project_id).all()
    if not letters:
        raise HTTPException(status_code=404, detail="No callback letters to export")

    doc_svc = DocumentService()
    l_dicts = [
        {
            "character_name": l.character_name,
            "role_type": l.role_type,
            "actor_name": l.actor_name,
            "letter_body": l.letter_body
        }
        for l in letters
    ]
    pdf_bytes = doc_svc.generate_callback_letters_pdf(l_dicts)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=10_Callback_Letters.pdf"}
    )

# -------------------------------------------------------------
# Complete Package & Individual Exports
# -------------------------------------------------------------
@router.get("/export/package")
def download_complete_package(project_id: int, db: Session = Depends(get_db)):
    """
    Downloads the Complete Pre-Production Package as a .ZIP archive containing:
    01_Script_Breakdown.pdf
    02_Scene_Breakdown.xlsx
    03_Cast_Breakdown.xlsx
    04_Location_Breakdown.xlsx
    05_Production_Elements.xlsx
    06_Shooting_Schedule.xlsx
    07_Stripboard.pdf
    08_Budget.xlsx
    09_Call_Sheets.pdf
    10_Callback_Letters.pdf
    11_Pre_Production_Report.pdf
    complete_project.json
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.scene_number).all()
    characters = db.query(Character).filter(Character.project_id == project_id).all()
    locations = db.query(Location).filter(Location.project_id == project_id).all()
    elements = db.query(ProductionElement).filter(ProductionElement.project_id == project_id).all()
    schedule = db.query(Schedule).filter(Schedule.project_id == project_id).first()
    budget = db.query(Budget).filter(Budget.project_id == project_id).first()
    call_sheets = db.query(CallSheet).filter(CallSheet.project_id == project_id).all()
    callback_letters = db.query(CallbackLetter).filter(CallbackLetter.project_id == project_id).all()

    doc_svc = DocumentService()

    # Convert to standard dicts
    p_dict = {"name": project.name, "director": project.director, "producer": project.producer, "genre": project.genre}
    sc_dicts = [
        {
            "id": s.id, "scene_number": s.scene_number, "heading": s.heading,
            "interior_exterior": s.interior_exterior, "location_name": s.location_name,
            "time_of_day": s.time_of_day, "estimated_pages": s.estimated_pages,
            "estimated_duration_minutes": s.estimated_duration_minutes,
            "complexity_level": s.complexity_level, "characters": []
        }
        for s in scenes
    ]
    char_dicts = [
        {
            "id": c.id, "name": c.name, "role": c.role, "scene_count": c.scene_count,
            "dialogue_count": c.dialogue_count, "estimated_screen_time_minutes": c.estimated_screen_time_minutes,
            "required_shooting_days": c.required_shooting_days, "costume_requirements": c.costume_requirements
        }
        for c in characters
    ]
    loc_dicts = [
        {
            "name": l.name, "interior_exterior": l.interior_exterior, "day_night": l.day_night,
            "scene_count": l.scene_count, "required_days": l.required_days,
            "company_move_required": l.company_move_required, "estimated_cost": l.estimated_cost
        }
        for l in locations
    ]
    elem_dicts = [
        {
            "category": e.category, "name": e.name, "quantity": e.quantity,
            "confidence": e.confidence, "extraction_source": e.extraction_source,
            "description": e.description, "scene_id": e.scene_id
        }
        for e in elements
    ]

    sched_dict = {
        "total_days": schedule.total_days if schedule else 0,
        "total_hours": schedule.total_shooting_hours if schedule else 0.0,
        "total_company_moves": schedule.total_company_moves if schedule else 0,
        "optimization_status": schedule.optimization_status if schedule else "OPTIMAL",
        "explanation": schedule.notes if schedule else "",
        "shooting_days": []
    }
    if schedule:
        for d in schedule.shooting_days:
            sched_dict["shooting_days"].append({
                "day_number": d.day_number,
                "shoot_date": d.shoot_date,
                "call_time": d.call_time,
                "wrap_time": d.wrap_time,
                "meal_break_time": d.meal_break_time,
                "total_shooting_hours": d.total_shooting_hours,
                "company_moves_count": d.company_moves_count,
                "scheduled_scenes": [
                    {
                        "sequence_order": ss.sequence_order,
                        "scene_number": ss.scene.scene_number if ss.scene else 1,
                        "heading": ss.scene.heading if ss.scene else "",
                        "location_name": ss.location_name,
                        "estimated_start_time": ss.estimated_start_time,
                        "estimated_duration_minutes": ss.estimated_duration_minutes,
                        "company_move_before": ss.company_move_before
                    }
                    for ss in d.scheduled_scenes
                ]
            })

    b_dict = {
        "subtotal": budget.subtotal if budget else 0.0,
        "contingency_rate": budget.contingency_rate if budget else 0.1,
        "contingency_amount": budget.contingency_amount if budget else 0.0,
        "tax_rate": budget.tax_rate if budget else 0.08,
        "tax_amount": budget.tax_amount if budget else 0.0,
        "grand_total": budget.grand_total if budget else 0.0,
        "disclaimer": budget.disclaimer if budget else "Illustrative planning estimates — user configurable.",
        "items": [
            {
                "category": i.category, "department": i.department, "account_code": i.account_code,
                "description": i.description, "quantity": i.quantity, "unit": i.unit,
                "unit_rate": i.unit_rate, "days_count": i.days_count, "subtotal": i.subtotal,
                "notes": i.notes
            }
            for i in (budget.items if budget else [])
        ]
    }

    cs_dicts = [
        {
            "project_name": project.name,
            "day_number": cs.day_number,
            "shoot_date": cs.shoot_date,
            "general_call_time": cs.general_call_time,
            "location_name": cs.location_name,
            "location_address": cs.location_address,
            "parking_info": cs.parking_info,
            "weather_placeholder": cs.weather_placeholder,
            "nearest_hospital": cs.nearest_hospital,
            "scenes_summary": cs.scenes_summary or [],
            "cast_calls": cs.cast_calls or [],
            "crew_calls": cs.crew_calls or [],
            "special_instructions": cs.special_instructions,
            "meal_break": cs.meal_break,
            "emergency_contact": cs.emergency_contact
        }
        for cs in call_sheets
    ]

    cb_dicts = [
        {
            "character_name": l.character_name,
            "role_type": l.role_type,
            "actor_name": l.actor_name,
            "letter_body": l.letter_body
        }
        for l in callback_letters
    ]

    zip_bytes = doc_svc.build_complete_package_zip(
        project=p_dict,
        scenes=sc_dicts,
        characters=char_dicts,
        locations=loc_dicts,
        elements=elem_dicts,
        schedule=sched_dict,
        budget=b_dict,
        call_sheets=cs_dicts,
        callback_letters=cb_dicts
    )

    clean_proj_name = project.name.replace(" ", "_")
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={clean_proj_name}_PreProduction_Package.zip"}
    )
