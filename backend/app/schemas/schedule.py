from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ScheduledSceneResponse(BaseModel):
    id: int
    scene_id: int
    sequence_order: int
    estimated_start_time: str
    estimated_duration_minutes: int
    setup_time_minutes: int
    location_name: Optional[str] = None
    company_move_before: bool
    notes: Optional[str] = None
    
    # Nested scene details
    scene_number: Optional[int] = None
    heading: Optional[str] = None
    first_line: Optional[str] = None
    interior_exterior: Optional[str] = None
    time_of_day: Optional[str] = None
    pages: Optional[float] = None
    complexity_level: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ShootingDayResponse(BaseModel):
    id: int
    day_number: int
    shoot_date: Optional[str] = None
    call_time: str
    wrap_time: str
    meal_break_time: str
    total_shooting_hours: float
    company_moves_count: int
    primary_location: Optional[str] = None
    cast_ids: Optional[List[Any]] = []
    equipment_ids: Optional[List[Any]] = []
    notes: Optional[str] = None
    scheduled_scenes: Optional[List[ScheduledSceneResponse]] = []

    model_config = ConfigDict(from_attributes=True)

class ScheduleResponse(BaseModel):
    id: int
    project_id: int
    name: str
    total_days: int
    total_shooting_hours: float
    total_company_moves: int
    optimization_status: str
    solver_time_seconds: float
    objective_value: float
    notes: Optional[str] = None
    created_at: datetime
    shooting_days: Optional[List[ShootingDayResponse]] = []

    model_config = ConfigDict(from_attributes=True)

class ScheduleOptimizeRequest(BaseModel):
    max_daily_hours: Optional[float] = 10.0
    include_setup_time: Optional[bool] = True
    prioritize_locations: Optional[bool] = True
