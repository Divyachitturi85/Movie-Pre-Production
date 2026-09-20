from fastapi import APIRouter, Depends, HTTPException
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
from app.models.explainability import AIExplainabilityRecord

router = APIRouter(prefix="/projects/{project_id}/reports", tags=["Reports"])

@router.get("")
def get_comprehensive_report(project_id: int, db: Session = Depends(get_db)):
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
    explain_records = db.query(AIExplainabilityRecord).filter(AIExplainabilityRecord.project_id == project_id).all()

    # Aggregate categories
    elements_by_cat = {}
    for el in elements:
        elements_by_cat[el.category] = elements_by_cat.get(el.category, 0) + 1

    # Complexity distribution
    comp_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "VERY HIGH": 0}
    for s in scenes:
        level = s.complexity_level or "LOW"
        comp_dist[level] = comp_dist.get(level, 0) + 1

    # Night scenes
    night_scenes_count = sum(1 for s in scenes if "NIGHT" in (s.time_of_day or "").upper())
    ext_scenes_count = sum(1 for s in scenes if "EXT" in (s.interior_exterior or "").upper())

    # Production risks
    risks = []
    if night_scenes_count > 0:
        risks.append({
            "risk": f"{night_scenes_count} Night Shoot Scenes",
            "severity": "MEDIUM",
            "mitigation": "Schedule night shoots consecutively; provide minimum 12-hour turnaround rest between shifts."
        })
    if elements_by_cat.get("VFX", 0) > 0:
        risks.append({
            "risk": f"{elements_by_cat.get('VFX')} CGI / Visual Effects Shots Identified",
            "severity": "HIGH",
            "mitigation": "Engage on-set VFX Supervisor to capture HDRI chrome balls, camera tracking metadata, and clean plates."
        })
    if elements_by_cat.get("WEAPON", 0) > 0:
        risks.append({
            "risk": f"{elements_by_cat.get('WEAPON')} Weapon & Firearm Sequences",
            "severity": "CRITICAL",
            "mitigation": "Certified licensed armorer required on set; enforce strict cold-weapon checks and lockbox storage."
        })
    if elements_by_cat.get("VEHICLE", 0) > 0:
        risks.append({
            "risk": f"{elements_by_cat.get('VEHICLE')} Moving Vehicle Action",
            "severity": "HIGH",
            "mitigation": "Stunt coordinator, police road closure permits, and precision drivers mandatory."
        })

    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "genre": project.genre,
            "director": project.director,
            "producer": project.producer,
            "status": project.status
        },
        "statistics": {
            "total_scenes": len(scenes),
            "total_characters": len(characters),
            "total_locations": len(locations),
            "total_elements": len(elements),
            "elements_by_category": elements_by_cat,
            "night_scenes": night_scenes_count,
            "exterior_scenes": ext_scenes_count,
            "complexity_distribution": comp_dist
        },
        "schedule_summary": {
            "total_days": schedule.total_days if schedule else 0,
            "total_shooting_hours": schedule.total_shooting_hours if schedule else 0.0,
            "company_moves": schedule.total_company_moves if schedule else 0,
            "status": schedule.optimization_status if schedule else "NOT_OPTIMIZED",
            "solver_time_seconds": schedule.solver_time_seconds if schedule else 0.0,
            "algorithm": "Google OR-Tools CP-SAT (Constraint Programming)"
        },
        "budget_summary": {
            "currency": budget.currency if budget else "USD",
            "subtotal": budget.subtotal if budget else 0.0,
            "contingency_amount": budget.contingency_amount if budget else 0.0,
            "tax_amount": budget.tax_amount if budget else 0.0,
            "grand_total": budget.grand_total if budget else 0.0,
            "disclaimer": budget.disclaimer if budget else "Illustrative planning estimates — user configurable."
        },
        "call_sheets_count": len(call_sheets),
        "callback_letters_count": len(callback_letters),
        "production_risks": risks,
        "assumptions": [
            "10-hour standard maximum shoot days with 45-minute courtesy lunch.",
            "Standard union turnaround of 12 hours between consecutive shoot days.",
            "Cast day player rates benchmarked against SAG-AFTRA Modified Low Budget agreements.",
            "Locations allow sufficient access for electrical and grip staging trucks."
        ],
        "ai_tools_summary": {
            "ocr": "PaddleOCR (applied dynamically when scanned text density falls below 35%)",
            "linguistics": "spaCy (en_core_web_sm) for sentence segmentation, tokenization, POS, and noun chunks",
            "ner": "Hugging Face Transformers (BERT-NER token classification)",
            "scheduling": "Google OR-Tools CP-SAT for multi-objective integer optimization",
            "budgeting": "Movie Magic Budgeting-compatible chart of accounts & calculation engine",
            "explainability_records_count": len(explain_records)
        }
    }
