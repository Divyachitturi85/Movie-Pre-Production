import re
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.scene import Scene
from app.models.character import Character
from app.models.location import Location
from app.models.production_element import ProductionElement
from app.models.explainability import AIExplainabilityRecord
from app.schemas.scene import SceneResponse
from app.schemas.character import CharacterResponse, CharacterUpdate
from app.schemas.location import LocationResponse
from app.schemas.production_element import ProductionElementResponse, ProductionElementCreate
from app.services.nlp_service import NLPService
from app.services.complexity_service import ComplexityService
from app.services.character_service import CharacterService, BLACKLIST, STANDALONE_TITLES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects/{project_id}", tags=["Analysis & Breakdown"])

@router.post("/analyze")
def run_nlp_analysis(project_id: int, db: Session = Depends(get_db)):
    """
    Executes the full AI NLP & Breakdown Pipeline:
    - Hugging Face BERT-NER token classification
    - spaCy linguistic POS and noun chunk extraction
    - Clean Screenplay Cast Extraction & Canonical Entity Resolution
    - Scene complexity scoring (Low/Med/High/Very High)
    - Production element categorization (Props, Costumes, Vehicles, VFX/SFX, Equipment)
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.scene_number).all()
    if not scenes:
        raise HTTPException(status_code=400, detail="No scenes found to analyze. Please upload or parse a screenplay first.")

    nlp_svc = NLPService()
    complexity_svc = ComplexityService()

    # Clear previous analysis data
    db.query(ProductionElement).filter(ProductionElement.project_id == project_id).delete()
    db.query(Character).filter(Character.project_id == project_id).delete()
    db.query(Location).filter(Location.project_id == project_id).delete()
    db.query(AIExplainabilityRecord).filter(
        AIExplainabilityRecord.project_id == project_id,
        AIExplainabilityRecord.stage.in_(["NER_CHARACTER", "NER_LOCATION", "NER_PROP", "NER_COSTUME", "NER_VEHICLE", "NER_VFX", "NER_SFX", "NER_WEAPON", "RESOURCE_EQUIPMENT", "COMPLEXITY_SCORING"])
    ).delete()

    # 1. Discover verified dialogue speakers across the entire screenplay
    all_raw_cues = []
    for sc in scenes:
        cues = CharacterService.extract_speakers_from_text(sc.raw_content or "")
        all_raw_cues.extend(cues)

    canonical_cast, alias_map = CharacterService.resolve_cast(all_raw_cues)
    logger.info(f"Project {project_id} discovered canonical cast: {canonical_cast}")

    character_stats = {}
    location_stats = {}

    for sc in scenes:
        # Determine verified dialogue speakers for this scene
        scene_speakers = CharacterService.extract_speakers_from_text(sc.raw_content or "")
        scene_chars = set()
        for sp in scene_speakers:
            canon = alias_map.get(sp)
            if canon and canon not in BLACKLIST and canon not in STANDALONE_TITLES:
                scene_chars.add(canon)

        # Also detect presence of canonical cast mentioned in scene action text
        action_search_text = f"{sc.action_text or ''} {sc.raw_content or ''}".lower()
        for canon in canonical_cast:
            sub_words = [w.lower() for w in canon.split() if w not in STANDALONE_TITLES and len(w) > 2]
            if sub_words and any(re.search(r'\b' + re.escape(sw) + r'\b', action_search_text) for sw in sub_words):
                scene_chars.add(canon)

        final_scene_chars = sorted(list(scene_chars))

        sc_dict = {
            "scene_number": sc.scene_number,
            "heading": sc.heading,
            "interior_exterior": sc.interior_exterior,
            "location_name": sc.location_name,
            "time_of_day": sc.time_of_day,
            "estimated_pages": sc.estimated_pages,
            "raw_content": sc.raw_content,
            "action_text": sc.action_text,
            "characters": final_scene_chars
        }

        # Run NLP entity extraction
        elements, explains = nlp_svc.extract_scene_elements(sc_dict)
        
        # Calculate complexity
        score, level, factors, comp_explain = complexity_svc.calculate_scene_complexity(sc_dict, elements)
        sc.complexity_score = score
        sc.complexity_level = level
        sc.complexity_factors = factors

        # Save AI Explainability records
        for exp in explains:
            rec = AIExplainabilityRecord(
                project_id=project_id,
                stage=exp.get("stage", "NLP"),
                target_entity=exp.get("target_entity"),
                input_data=exp.get("input_data"),
                ai_method=exp.get("ai_method", "Transformer + spaCy"),
                output_detected=exp.get("output_detected"),
                confidence=exp.get("confidence", 0.9),
                fallback_used=exp.get("fallback_used", False),
                fallback_reason=exp.get("fallback_reason"),
                details=exp.get("details", {})
            )
            db.add(rec)

        db.add(AIExplainabilityRecord(
            project_id=project_id,
            stage=comp_explain["stage"],
            target_entity=comp_explain["target_entity"],
            input_data=comp_explain["input_data"],
            ai_method=comp_explain["ai_method"],
            output_detected=comp_explain["output_detected"],
            confidence=comp_explain["confidence"],
            fallback_used=comp_explain["fallback_used"],
            details=comp_explain["details"]
        ))

        # Save Production Elements
        for el in elements:
            pe = ProductionElement(
                project_id=project_id,
                scene_id=sc.id,
                category=el.get("category", "PROP"),
                name=el.get("name", "Asset"),
                description=el.get("description", ""),
                quantity=el.get("quantity", 1),
                confidence=el.get("confidence", 0.88),
                extraction_source=el.get("extraction_source", "NLP_SERVICE")
            )
            db.add(pe)

        # Aggregate Characters
        for c_name in final_scene_chars:
            stat = character_stats.setdefault(c_name, {"scenes": set(), "dialogues": 0})
            stat["scenes"].add(sc.scene_number)
            if c_name in scene_speakers or any(alias_map.get(sp) == c_name for sp in scene_speakers):
                stat["dialogues"] += 2

        # Aggregate Locations
        loc_name = sc.location_name or "MAIN SET"
        l_stat = location_stats.setdefault(loc_name, {"scenes": [], "ie": sc.interior_exterior, "dn": sc.time_of_day})
        l_stat["scenes"].append(sc.scene_number)

    # Save resolved canonical Characters (purging non-characters, aliases, and titles)
    resolved_char_stats = CharacterService.resolve_character_stats(character_stats)
    for c_name, stat in resolved_char_stats.items():
        sc_list = stat["scenes"]
        sc_cnt = len(sc_list)
        profile = CharacterService.get_character_profile(
            name=c_name,
            scene_count=sc_cnt,
            dialogue_count=stat["dialogues"],
            genre=project.genre
        )
        c_mod = Character(
            project_id=project_id,
            name=c_name,
            role=profile["role"],
            scene_count=sc_cnt,
            dialogue_count=stat["dialogues"],
            estimated_screen_time_minutes=profile["estimated_screen_time_minutes"],
            required_shooting_days=profile["required_shooting_days"],
            costume_requirements=profile["costume_requirements"],
            makeup_requirements=profile["makeup_requirements"],
            scene_ids=sc_list
        )
        db.add(c_mod)

    # Save aggregated Locations
    for loc_name, l_stat in location_stats.items():
        loc_mod = Location(
            project_id=project_id,
            name=loc_name,
            interior_exterior=l_stat["ie"],
            day_night=l_stat["dn"],
            scene_count=len(l_stat["scenes"]),
            required_days=max(1, (len(l_stat["scenes"]) + 2) // 3),
            company_move_required=len(l_stat["scenes"]) < 3,
            estimated_cost=2000.0 if "EXT" in l_stat["ie"] else 1200.0,
            address_or_description=f"Studio Stage / Practical Location - {loc_name}",
            scene_ids=l_stat["scenes"]
        )
        db.add(loc_mod)

    project.status = "ANALYZED"
    project.current_stage = "BREAKDOWN_COMPLETE"
    db.commit()

    return {
        "status": "SUCCESS",
        "message": f"Analyzed {len(scenes)} scenes successfully.",
        "characters_extracted": len(resolved_char_stats),
        "locations_extracted": len(location_stats),
        "total_elements": db.query(ProductionElement).filter(ProductionElement.project_id == project_id).count()
    }

@router.get("/scenes", response_model=List[SceneResponse])
def get_scenes(project_id: int, db: Session = Depends(get_db)):
    # Auto-run analysis if project has scenes but 0 production elements exist
    scene_count = db.query(Scene).filter(Scene.project_id == project_id).count()
    element_count = db.query(ProductionElement).filter(ProductionElement.project_id == project_id).count()
    if scene_count > 0 and element_count == 0:
        try:
            run_nlp_analysis(project_id, db)
        except Exception as e:
            logger.warning(f"Auto-analysis on get_scenes failed: {e}")

    scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.scene_number).all()
    return scenes

@router.get("/scenes/{scene_id}", response_model=SceneResponse)
def get_scene(project_id: int, scene_id: int, db: Session = Depends(get_db)):
    scene = db.query(Scene).filter(Scene.project_id == project_id, Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene

@router.get("/characters", response_model=List[CharacterResponse])
def get_characters(project_id: int, db: Session = Depends(get_db)):
    characters = db.query(Character).filter(Character.project_id == project_id).order_by(Character.scene_count.desc()).all()
    return characters

@router.put("/characters/{char_id}", response_model=CharacterResponse)
def update_character(project_id: int, char_id: int, payload: CharacterUpdate, db: Session = Depends(get_db)):
    char = db.query(Character).filter(Character.project_id == project_id, Character.id == char_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if payload.role is not None:
        char.role = payload.role
    if payload.costume_requirements is not None:
        char.costume_requirements = payload.costume_requirements
    if payload.makeup_requirements is not None:
        char.makeup_requirements = payload.makeup_requirements
    if payload.notes is not None:
        char.notes = payload.notes

    db.commit()
    db.refresh(char)
    return char

@router.get("/locations", response_model=List[LocationResponse])
def get_locations(project_id: int, db: Session = Depends(get_db)):
    locations = db.query(Location).filter(Location.project_id == project_id).order_by(Location.scene_count.desc()).all()
    return locations

@router.get("/elements", response_model=List[ProductionElementResponse])
def get_elements(
    project_id: int,
    category: Optional[str] = Query(None),
    scene_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    # Auto-run analysis if project has scenes but 0 production elements exist
    scene_count = db.query(Scene).filter(Scene.project_id == project_id).count()
    element_count = db.query(ProductionElement).filter(ProductionElement.project_id == project_id).count()
    if scene_count > 0 and element_count == 0:
        try:
            run_nlp_analysis(project_id, db)
        except Exception as e:
            logger.warning(f"Auto-analysis on get_elements failed: {e}")

    query = db.query(ProductionElement).filter(ProductionElement.project_id == project_id)
    if category:
        query = query.filter(ProductionElement.category == category.upper())
    if scene_id:
        query = query.filter(ProductionElement.scene_id == scene_id)
    return query.order_by(ProductionElement.category, ProductionElement.name).all()

@router.post("/elements", response_model=ProductionElementResponse)
def create_element(project_id: int, payload: ProductionElementCreate, db: Session = Depends(get_db)):
    pe = ProductionElement(
        project_id=project_id,
        scene_id=payload.scene_id,
        category=payload.category.upper(),
        name=payload.name,
        description=payload.description,
        quantity=payload.quantity,
        confidence=payload.confidence,
        extraction_source="USER_ADDED"
    )
    db.add(pe)
    db.commit()
    db.refresh(pe)
    return pe

@router.delete("/elements/{element_id}")
def delete_element(project_id: int, element_id: int, db: Session = Depends(get_db)):
    pe = db.query(ProductionElement).filter(ProductionElement.project_id == project_id, ProductionElement.id == element_id).first()
    if not pe:
        raise HTTPException(status_code=404, detail="Element not found")
    db.delete(pe)
    db.commit()
    return {"status": "DELETED"}
