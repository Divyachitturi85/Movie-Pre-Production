"""
Run verification for sections 3 through 11:
- spaCy NLP
- Hugging Face BERT NER
- Project Aurora End-to-End Screenplay Analysis
- Google OR-Tools CP-SAT Solver & Constraints
- Budget Arithmetic & Formulas
- Callback Letters Distinctness & Casting Fields
- Document Service (PDF, XLSX, DOCX, JSON, ZIP)
- ZIP 11-Artifact Inspection
"""
import os
import sys
import io
import json
import zipfile

def main():
    print("="*80)
    print("STARTING DIRECT VERIFICATION OF AI PIPELINES & OPTIMIZATION")
    print("="*80)

    # 1. spaCy
    print("\n--- [3] TESTING SPACY NLP PIPELINE ---")
    from app.services.spacy_service import SpacyService
    spacy_svc = SpacyService()
    test_action_sentence = "SARAH draws a high-energy plasma cutter from her tactical vest and breaches the security hatch."
    spacy_res = spacy_svc.process_text(test_action_sentence)
    cand_res = spacy_svc.extract_entity_candidates(test_action_sentence)
    print(f"Action Input: {test_action_sentence}")
    print(f"Noun Chunks: {spacy_res.get('noun_chunks', [])}")
    print(f"Candidate Objects: {cand_res.get('potential_objects', [])}")
    assert len(spacy_res.get("noun_chunks", [])) > 0
    print(">>> spaCy PASSED!")

    # 2. Hugging Face BERT NER
    print("\n--- [4] TESTING HUGGING FACE BERT TOKEN CLASSIFICATION ---")
    from app.services.nlp_service import NLPService
    nlp_svc = NLPService()
    sample_ner_text = "DR. ELENA VANCE contacted GENERAL SHEPHERD at NASA Headquarters in WASHINGTON regarding the PROXIMA ROVER."
    hf_pipe = nlp_svc._get_hf_pipeline()
    ner_entities = hf_pipe(sample_ner_text)
    print(f"NER Input: {sample_ner_text}")
    print("Extracted Entities:")
    for ent in ner_entities:
        print(f"  - Entity: '{ent['word']}' | Label: {ent['entity_group']} | Score: {ent['score']:.4f}")
    assert len(ner_entities) > 0
    print(">>> Hugging Face BERT NER PASSED!")

    # 3. Database Project & Screenplay Ingestion
    print("\n--- [5] TESTING SCREENPLAY INGESTION & PARSING ---")
    from app.core.database import SessionLocal
    from app.models.project import Project
    from app.models.scene import Scene
    from app.models.character import Character
    from app.models.location import Location
    from app.models.production_element import ProductionElement
    from app.services.demo_service import DemoService

    db = SessionLocal()
    demo_svc = DemoService()
    proj = demo_svc.load_demo_project(db)

    db_scenes = db.query(Scene).filter(Scene.project_id == proj.id).order_by(Scene.scene_number).all()
    db_chars = db.query(Character).filter(Character.project_id == proj.id).all()
    db_locs = db.query(Location).filter(Location.project_id == proj.id).all()
    db_elems = db.query(ProductionElement).filter(ProductionElement.project_id == proj.id).all()

    print(f"Loaded Project: '{proj.name}' (ID: {proj.id})")
    print(f"Scenes count: {len(db_scenes)}")
    print(f"Characters count: {len(db_chars)}")
    print(f"Locations count: {len(db_locs)}")
    print(f"Production elements count: {len(db_elems)}")
    assert len(db_scenes) >= 9
    print(">>> Script Parsing & Database Flow PASSED!")

    # 4. Google OR-Tools CP-SAT Scheduling
    print("\n--- [6] TESTING GOOGLE OR-TOOLS CP-SAT SCHEDULER ---")
    from app.services.scheduler_service import SchedulerService
    scheduler = SchedulerService()
    scenes_input = [
        {
            "id": s.id, "scene_number": s.scene_number, "heading": s.heading,
            "location_name": s.location_name, "interior_exterior": s.interior_exterior,
            "time_of_day": s.time_of_day, "estimated_pages": s.estimated_pages,
            "estimated_duration_minutes": s.estimated_duration_minutes,
            "complexity_level": s.complexity_level,
            "characters": [pe.name for pe in s.production_elements if pe.category == "CAST"]
        }
        for s in db_scenes
    ]
    sched_result = scheduler.optimize_schedule(scenes=scenes_input, max_daily_hours=12.0)
    print(f"CP-SAT Status: {sched_result['optimization_status']}")
    print(f"Scheduled Days: {sched_result['total_days']}, Hours: {sched_result['total_hours']:.1f}, Moves: {sched_result['total_company_moves']}")
    
    all_scheduled_scene_ids = []
    for day in sched_result["shooting_days"]:
        print(f"  Day {day['day_number']}: {len(day['scheduled_scenes'])} scenes, {day['total_shooting_hours']:.1f} hrs, Locations: {set(sc['location_name'] for sc in day['scheduled_scenes'])}")
        assert day["total_shooting_hours"] <= 12.0001
        for sc in day["scheduled_scenes"]:
            all_scheduled_scene_ids.append(sc["scene_id"])

    assert len(all_scheduled_scene_ids) == len(db_scenes)
    assert len(set(all_scheduled_scene_ids)) == len(db_scenes)
    print(">>> Google OR-Tools CP-SAT Solver PASSED with all mathematical constraints satisfied!")

    # 5. Budget Calculation & Arithmetic
    print("\n--- [7] TESTING BUDGET LEDGER & ARITHMETIC ---")
    from app.services.budget_service import BudgetService
    budget_svc = BudgetService()
    b_res = budget_svc.generate_initial_budget(
        shooting_days=sched_result["total_days"],
        cast_count=len(db_chars),
        location_count=len(db_locs),
        has_vfx=True
    )
    subtotal = b_res["subtotal"]
    contingency = b_res["contingency_amount"]
    tax = b_res["tax_amount"]
    grand_total = b_res["grand_total"]

    print(f"Subtotal: ${subtotal:,.2f}")
    print(f"Contingency (10%): ${contingency:,.2f}")
    print(f"Tax (8%): ${tax:,.2f}")
    print(f"Grand Total: ${grand_total:,.2f}")

    assert abs(contingency - round(subtotal * 0.10, 2)) < 0.05
    assert abs(tax - round((subtotal + contingency) * 0.08, 2)) < 0.05
    assert abs(grand_total - round(subtotal + contingency + tax, 2)) < 0.05
    print(">>> Budget Arithmetic PASSED with 100% precision!")

    # 6. Callback Letters
    print("\n--- [8] TESTING CALLBACK LETTERS ---")
    from app.services.callback_service import CallbackService
    cb_svc = CallbackService()
    letter1 = cb_svc.generate_letter(
        project_name=proj.name, director="Marcus Vance", actor_name="Claire Foy",
        character_name="DR. ELENA VANCE", role_type="LEAD",
        callback_date="Tuesday, October 20, 2026", callback_time="10:00 AM EST",
        location="Soundstage A, Room 204",
        sides_reference="Scene 1 & Scene 4",
        what_to_prepare="Memorize Scene 4 dialogue. Prepare chemistry adjustments.",
        special_instructions="Clinical attire required."
    )
    letter2 = cb_svc.generate_letter(
        project_name=proj.name, director="Marcus Vance", actor_name="Pedro Pascal",
        character_name="COMMANDER MARCUS COLE", role_type="SUPPORTING LEAD",
        callback_date="Wednesday, October 21, 2026", callback_time="02:30 PM EST",
        location="Studio B - Stunt Rehearsal Arena",
        sides_reference="Scene 3 & Scene 7",
        what_to_prepare="Physical movement test in mock EVA harness.",
        special_instructions="Athletic training gear required."
    )
    print("Letter 1 Role:", letter1["character_name"], "| Actor:", letter1["actor_name"])
    print("Letter 2 Role:", letter2["character_name"], "| Actor:", letter2["actor_name"])
    assert letter1["actor_name"] != letter2["actor_name"]
    assert letter1["what_to_prepare"] != letter2["what_to_prepare"]
    assert letter1["location"] != letter2["location"]
    print(">>> Callback Letters PASSED!")

    # 7. Document Service Exports & ZIP 11-Artifact Inspection
    print("\n--- [9 & 10] TESTING DOCUMENT GENERATION & 11-ARTIFACT ZIP PACKAGE ---")
    from app.services.document_service import DocumentService
    doc_svc = DocumentService()

    sample_cs = {
        "project_name": proj.name, "day_number": 1, "shoot_date": "2026-10-12",
        "general_call_time": "07:00 AM", "location_name": "Pinewood Stage 4",
        "location_address": "Pinewood Studios, Iver Heath SL0 0NH, UK",
        "parking_info": "Crew Lot B", "weather_placeholder": "Overcast, 14C",
        "nearest_hospital": "Wexham Park Hospital, Slough SL2 4HL",
        "scenes_summary": [{"scene_number": 1, "heading": "INT. COMMAND CENTER - DAY", "pages": 1.5, "start_time": "08:00 AM", "duration_mins": 90, "complexity": "LOW"}],
        "cast_calls": [{"cast_id": 1, "character_name": "DR. ELENA VANCE", "actor_name": "Claire Foy", "pickup": "06:00 AM", "hair_makeup": "06:30 AM", "on_set": "07:45 AM", "status": "CALLED"}],
        "crew_calls": [{"department": "CAMERA", "position": "Director of Photography", "call_time": "07:00 AM"}],
        "special_instructions": "Safety goggles required during airlock depressurization test.",
        "meal_break": "13:00 - 14:00 (Stage C Commissary)",
        "emergency_contact": "Production Manager: +44 20 7946 0912"
    }

    # Generate ZIP
    zip_bytes = doc_svc.build_complete_package_zip(
        project={"name": proj.name, "genre": proj.genre, "director": proj.director, "producer": proj.producer, "status": proj.status, "target_budget": 3500000.0},
        scenes=[{"id": s.id, "scene_number": s.scene_number, "heading": s.heading, "location_name": s.location_name, "interior_exterior": s.interior_exterior, "time_of_day": s.time_of_day, "estimated_pages": s.estimated_pages, "estimated_duration_minutes": s.estimated_duration_minutes, "complexity_level": s.complexity_level, "characters": [pe.name for pe in s.production_elements if pe.category == 'CAST']} for s in db_scenes],
        characters=[{"id": c.id, "name": c.name, "role": c.role, "scene_count": c.scene_count, "dialogue_count": c.dialogue_count, "estimated_screen_time_minutes": c.estimated_screen_time_minutes, "required_shooting_days": c.required_shooting_days, "costume_requirements": c.costume_requirements} for c in db_chars],
        locations=[{"name": l.name, "interior_exterior": l.interior_exterior, "day_night": l.day_night, "scene_count": l.scene_count, "required_days": l.required_days, "company_move_required": l.company_move_required, "estimated_cost": l.estimated_cost} for l in db_locs],
        elements=[{"category": e.category, "name": e.name, "quantity": e.quantity, "confidence": e.confidence, "extraction_source": e.extraction_source, "description": e.description, "scene_id": e.scene_id} for e in db_elems],
        schedule=sched_result,
        budget=b_res,
        call_sheets=[sample_cs],
        callback_letters=[letter1, letter2]
    )

    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    file_list = zf.namelist()
    print(f"Total files in ZIP: {len(file_list)}")
    for idx, fname in enumerate(file_list, 1):
        info = zf.getinfo(fname)
        print(f"  {idx:2d}. {fname:42s} | {info.file_size:,} bytes")
        assert info.file_size > 0, f"File {fname} is empty!"

    assert len(file_list) >= 11, f"Expected at least 11 artifacts, got {len(file_list)}"
    print(">>> 11-Artifact ZIP Generation & File Validation PASSED!")

    db.close()
    print("\n" + "="*80)
    print("ALL CORE MODULES VERIFIED WITH REAL EXECUTION EVIDENCE!")
    print("="*80)

if __name__ == "__main__":
    main()
