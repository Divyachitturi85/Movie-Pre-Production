import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.project import Project
from app.models.character import Character
from app.services.demo_service import DemoService
from app.api.analysis import run_nlp_analysis

db = SessionLocal()
try:
    print("=== 1. Reloading Demo Project (Project Aurora) ===")
    demo_svc = DemoService()
    p4 = demo_svc.load_demo_project(db)
    print(f"Project Aurora reloaded with ID: {p4.id}")

    # Print characters for Project Aurora
    aurora_chars = db.query(Character).filter(Character.project_id == p4.id).all()
    print("Project Aurora Characters:")
    for c in aurora_chars:
        print(f"  - {c.name} | Role: {c.role} | Scenes: {c.scene_count} ({c.scene_ids}) | Days: {c.required_shooting_days}")

    print("\n=== 2. Re-running NLP Analysis for Other Projects ===")
    other_projects = db.query(Project).filter(Project.id != p4.id).all()
    for proj in other_projects:
        print(f"\nRe-analyzing Project {proj.id}: {proj.name}...")
        try:
            res = run_nlp_analysis(proj.id, db)
            print(f"  Result: {res}")
            chars = db.query(Character).filter(Character.project_id == proj.id).all()
            print(f"  Characters ({len(chars)}):")
            for c in chars:
                print(f"    - {c.name} | Role: {c.role} | Scenes: {c.scene_count} ({c.scene_ids}) | Days: {c.required_shooting_days}")
        except Exception as e:
            print(f"  Error analyzing project {proj.id}: {e}")

finally:
    db.close()

