import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.config import settings

def main():
    parser = argparse.ArgumentParser(
        description="Re-analyzes screenplay projects in the database. CAUTION: Destructive operation."
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Explicit confirmation required to execute database mutations and NLP re-analysis."
    )
    args = parser.parse_args()

    # Resolve database target path
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///./") or db_url.startswith("sqlite:///"):
        raw_path = db_url.replace("sqlite:///", "")
        resolved_db_path = os.path.abspath(raw_path)
    else:
        resolved_db_path = db_url

    print("=" * 70)
    print("MOVIE PRE-PRODUCTION SYSTEM: DATABASE RE-ANALYSIS UTILITY")
    print("=" * 70)
    print(f"Target Database URL:  {db_url}")
    print(f"Target Database File: {resolved_db_path}")
    print("=" * 70)

    if not args.confirm:
        print("\n[WARNING] SAFETY INTERLOCK ACTIVATED:")
        print("This script is a destructive developer maintenance utility that will:")
        print("  1. Completely reset 'Project Aurora' (delete and re-seed from demo spec).")
        print("  2. Re-run NLP screenplay parsing on ALL other projects in this database.")
        print("  3. OVERWRITE any manual edits to characters, locations, scenes, budgets, and schedules.")
        print("\nOperation aborted. No changes have been made to the database.")
        print("To proceed, you must run this script with explicit confirmation:")
        print("    python backend/reanalyze_all.py --confirm\n")
        sys.exit(0)

    print("\n[CONFIRMED] Proceeding with database re-analysis...")

    from app.core.database import SessionLocal, engine, Base
    import app.models  # Ensures all models are registered with Base
    from app.models.project import Project
    from app.models.character import Character
    from app.services.demo_service import DemoService
    from app.api.analysis import run_nlp_analysis

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("\n=== 1. Reloading Demo Project (Project Aurora) ===")
        demo_svc = DemoService()
        p4 = demo_svc.load_demo_project(db)
        print(f"Project Aurora reloaded with ID: {p4.id}")

        # Print characters for Project Aurora
        aurora_chars = db.query(Character).filter(Character.project_id == p4.id).all()
        print(f"Project Aurora Characters ({len(aurora_chars)}):")
        for c in aurora_chars:
            print(f"  - {c.name} | Role: {c.role} | Scenes: {c.scene_count} ({c.scene_ids}) | Days: {c.required_shooting_days}")

        print("\n=== 2. Re-running NLP Analysis for Other Projects ===")
        other_projects = db.query(Project).filter(Project.id != p4.id).all()
        if not other_projects:
            print("No additional projects to re-analyze.")
        for proj in other_projects:
            print(f"\nRe-analyzing Project {proj.id}: '{proj.name}'...")
            try:
                res = run_nlp_analysis(proj.id, db)
                print(f"  Status: {res.get('status', 'Completed') if isinstance(res, dict) else 'Completed'}")
                chars = db.query(Character).filter(Character.project_id == proj.id).all()
                print(f"  Characters ({len(chars)}):")
                for c in chars:
                    print(f"    - {c.name} | Role: {c.role} | Scenes: {c.scene_count} ({c.scene_ids}) | Days: {c.required_shooting_days}")
            except Exception as e:
                print(f"  [ERROR] Analyzing project {proj.id}: {e}")

        print("\nDatabase re-analysis complete.")

    finally:
        db.close()

if __name__ == "__main__":
    main()

