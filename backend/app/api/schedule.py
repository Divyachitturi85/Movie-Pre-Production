from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.scene import Scene
from app.models.schedule import Schedule
from app.models.shooting_day import ShootingDay
from app.models.scheduled_scene import ScheduledScene
from app.models.explainability import AIExplainabilityRecord
from app.schemas.schedule import ScheduleResponse, ScheduleOptimizeRequest
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/projects/{project_id}", tags=["Scheduling & Stripboard"])

@router.post("/schedule/optimize", response_model=ScheduleResponse)
def optimize_schedule(
    project_id: int,
    payload: ScheduleOptimizeRequest = ScheduleOptimizeRequest(),
    db: Session = Depends(get_db)
):
    """
    Solves shooting schedule optimization via Google OR-Tools CP-SAT solver.
    Minimizes shooting days, location company moves, and cast idle gaps.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.scene_number).all()
    if not scenes:
        raise HTTPException(status_code=400, detail="No scenes found to schedule.")

    scenes_data = []
    scene_db_map = {}
    for sc in scenes:
        # Extract cast names from production elements or text
        cast_chars = []
        for pe in sc.production_elements:
            if pe.category == "CAST":
                cast_chars.append(pe.name)

        s_dict = {
            "id": sc.id,
            "scene_number": sc.scene_number,
            "heading": sc.heading,
            "interior_exterior": sc.interior_exterior,
            "location_name": sc.location_name,
            "time_of_day": sc.time_of_day,
            "estimated_pages": sc.estimated_pages,
            "estimated_duration_minutes": sc.estimated_duration_minutes,
            "complexity_level": sc.complexity_level,
            "characters": cast_chars
        }
        scenes_data.append(s_dict)
        scene_db_map[sc.scene_number] = sc

    scheduler_svc = SchedulerService()
    sched_result = scheduler_svc.optimize_schedule(
        scenes=scenes_data,
        max_daily_hours=payload.max_daily_hours or 10.0,
        include_setup_time=payload.include_setup_time,
        prioritize_locations=payload.prioritize_locations
    )

    # Delete existing schedule if present
    db.query(Schedule).filter(Schedule.project_id == project_id).delete()

    schedule = Schedule(
        project_id=project_id,
        name="Optimized Production Schedule (Google OR-Tools CP-SAT)",
        total_days=sched_result["total_days"],
        total_shooting_hours=sched_result["total_hours"],
        total_company_moves=sched_result["total_company_moves"],
        optimization_status=sched_result["optimization_status"],
        solver_time_seconds=sched_result["solver_time_seconds"],
        objective_value=sched_result["objective_value"],
        notes=sched_result["explanation"]
    )
    db.add(schedule)
    db.flush()

    # Save shooting days and scheduled scenes
    for d_data in sched_result.get("shooting_days", []):
        shoot_day = ShootingDay(
            schedule_id=schedule.id,
            day_number=d_data["day_number"],
            shoot_date=d_data["shoot_date"],
            call_time=d_data["call_time"],
            wrap_time=d_data["wrap_time"],
            meal_break_time=d_data["meal_break_time"],
            total_shooting_hours=d_data["total_shooting_hours"],
            company_moves_count=d_data["company_moves_count"],
            primary_location=d_data["primary_location"],
            cast_ids=d_data["cast_ids"],
            equipment_ids=d_data["equipment_ids"],
            notes=d_data["notes"]
        )
        db.add(shoot_day)
        db.flush()

        for s_item in d_data.get("scheduled_scenes", []):
            sc_num = s_item.get("scene_number", 1)
            sc_ref = scene_db_map.get(sc_num)
            sc_id = sc_ref.id if sc_ref else s_item.get("scene_id", 1)

            scheduled_scene = ScheduledScene(
                shooting_day_id=shoot_day.id,
                scene_id=sc_id,
                sequence_order=s_item["sequence_order"],
                estimated_start_time=s_item["estimated_start_time"],
                estimated_duration_minutes=s_item["estimated_duration_minutes"],
                setup_time_minutes=s_item["setup_time_minutes"],
                location_name=s_item["location_name"],
                company_move_before=s_item["company_move_before"]
            )
            db.add(scheduled_scene)

    # Save AI Explainability record for OR-Tools
    explain_rec = AIExplainabilityRecord(
        project_id=project_id,
        stage="ORTOOLS_SCHEDULING",
        target_entity=f"Project Schedule ({sched_result['total_days']} Shoot Days)",
        input_data=f"{len(scenes)} scenes, max {payload.max_daily_hours} hrs/day",
        ai_method="Google OR-Tools CP-SAT (Constraint Programming Solver)",
        output_detected=f"Status: {sched_result['optimization_status']} | Days: {sched_result['total_days']} | Moves: {sched_result['total_company_moves']} | Solve Time: {sched_result['solver_time_seconds']}s",
        confidence=1.0,
        fallback_used=(sched_result["optimization_status"] == "HEURISTIC_FALLBACK"),
        fallback_reason="Heuristic fallback" if sched_result["optimization_status"] == "HEURISTIC_FALLBACK" else None,
        details={
            "objective_value": sched_result["objective_value"],
            "total_shooting_hours": sched_result["total_hours"],
            "total_company_moves": sched_result["total_company_moves"]
        }
    )
    db.add(explain_rec)

    project.status = "SCHEDULED"
    project.current_stage = "SCHEDULE_OPTIMIZED"
    db.commit()
    db.refresh(schedule)

    return get_schedule(project_id, db)

@router.get("/schedule", response_model=ScheduleResponse)
def get_schedule(project_id: int, db: Session = Depends(get_db)):
    schedule = db.query(Schedule).filter(Schedule.project_id == project_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule has not been generated yet")
    return schedule

@router.get("/stripboard")
def get_stripboard_data(project_id: int, db: Session = Depends(get_db)):
    """
    Returns Movie Magic-compatible stripboard data:
    Scene #, Heading, Location, INT/EXT, Day/Night, Pages, Duration, Complexity,
    and standard Film Industry Color Coding:
    - EXT. DAY: Yellow (#FEF08A)
    - INT. DAY: White (#FFFFFF)
    - EXT. NIGHT: Green (#BBF7D0)
    - INT. NIGHT: Blue (#BFDBFE)
    """
    scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.scene_number).all()
    schedule = db.query(Schedule).filter(Schedule.project_id == project_id).first()
    
    # Map scene to shooting day if scheduled
    scene_day_map = {}
    if schedule:
        for day in schedule.shooting_days:
            for sc in day.scheduled_scenes:
                scene_day_map[sc.scene_id] = day.day_number

    strips = []
    for sc in scenes:
        ie = (sc.interior_exterior or "INT").upper()
        tod = (sc.time_of_day or "DAY").upper()

        if "EXT" in ie and "NIGHT" in tod:
            color = "#BBF7D0"      # Green
            color_name = "Green (EXT. NIGHT)"
        elif "EXT" in ie:
            color = "#FEF08A"      # Yellow
            color_name = "Yellow (EXT. DAY)"
        elif "INT" in ie and "NIGHT" in tod:
            color = "#BFDBFE"      # Blue
            color_name = "Blue (INT. NIGHT)"
        else:
            color = "#FFFFFF"      # White
            color_name = "White (INT. DAY)"

        strips.append({
            "scene_id": sc.id,
            "scene_number": sc.scene_number,
            "heading": sc.heading,
            "location_name": sc.location_name,
            "interior_exterior": ie,
            "time_of_day": tod,
            "estimated_pages": sc.estimated_pages,
            "estimated_duration_minutes": sc.estimated_duration_minutes,
            "complexity_level": sc.complexity_level,
            "strip_color": color,
            "strip_color_name": color_name,
            "shooting_day": scene_day_map.get(sc.id, 1)
        })

    return {
        "disclaimer": "Movie Magic Scheduling-compatible production data",
        "total_strips": len(strips),
        "strips": strips
    }
