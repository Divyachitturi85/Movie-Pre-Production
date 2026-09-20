from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.scene import Scene
from app.models.character import Character
from app.models.location import Location
from app.models.schedule import Schedule
from app.models.budget import Budget
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.demo_service import DemoService

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    results = []
    for p in projects:
        sc_count = db.query(Scene).filter(Scene.project_id == p.id).count()
        char_count = db.query(Character).filter(Character.project_id == p.id).count()
        loc_count = db.query(Location).filter(Location.project_id == p.id).count()
        sched = db.query(Schedule).filter(Schedule.project_id == p.id).first()
        budg = db.query(Budget).filter(Budget.project_id == p.id).first()

        results.append(ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            genre=p.genre,
            director=p.director,
            producer=p.producer,
            status=p.status,
            current_stage=p.current_stage,
            created_at=p.created_at,
            updated_at=p.updated_at,
            scene_count=sc_count,
            character_count=char_count,
            location_count=loc_count,
            total_shooting_days=sched.total_days if sched else 0,
            estimated_budget=budg.grand_total if budg else 0.0
        ))
    return results

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        name=payload.name,
        description=payload.description,
        genre=payload.genre,
        director=payload.director,
        producer=payload.producer,
        status="CREATED",
        current_stage="INIT"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        genre=project.genre,
        director=project.director,
        producer=project.producer,
        status=project.status,
        current_stage=project.current_stage,
        created_at=project.created_at,
        updated_at=project.updated_at,
        scene_count=0,
        character_count=0,
        location_count=0,
        total_shooting_days=0,
        estimated_budget=0.0
    )

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    
    sc_count = db.query(Scene).filter(Scene.project_id == p.id).count()
    char_count = db.query(Character).filter(Character.project_id == p.id).count()
    loc_count = db.query(Location).filter(Location.project_id == p.id).count()
    sched = db.query(Schedule).filter(Schedule.project_id == p.id).first()
    budg = db.query(Budget).filter(Budget.project_id == p.id).first()

    return ProjectResponse(
        id=p.id,
        name=p.name,
        description=p.description,
        genre=p.genre,
        director=p.director,
        producer=p.producer,
        status=p.status,
        current_stage=p.current_stage,
        created_at=p.created_at,
        updated_at=p.updated_at,
        scene_count=sc_count,
        character_count=char_count,
        location_count=loc_count,
        total_shooting_days=sched.total_days if sched else 0,
        estimated_budget=budg.grand_total if budg else 0.0
    )

@router.post("/demo/load", response_model=ProjectResponse)
def load_demo_project_endpoint(db: Session = Depends(get_db)):
    """
    1-Click Demo Loader: Populates 'Project Aurora' complete with scenes,
    characters, locations, OR-Tools schedule, budget, call sheets, and callback letters.
    """
    demo_svc = DemoService()
    project = demo_svc.load_demo_project(db)
    
    sc_count = db.query(Scene).filter(Scene.project_id == project.id).count()
    char_count = db.query(Character).filter(Character.project_id == project.id).count()
    loc_count = db.query(Location).filter(Location.project_id == project.id).count()
    sched = db.query(Schedule).filter(Schedule.project_id == project.id).first()
    budg = db.query(Budget).filter(Budget.project_id == project.id).first()

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        genre=project.genre,
        director=project.director,
        producer=project.producer,
        status=project.status,
        current_stage=project.current_stage,
        created_at=project.created_at,
        updated_at=project.updated_at,
        scene_count=sc_count,
        character_count=char_count,
        location_count=loc_count,
        total_shooting_days=sched.total_days if sched else 0,
        estimated_budget=budg.grand_total if budg else 0.0
    )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(p)
    db.commit()
    return None
