from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CallSheetResponse(BaseModel):
    id: int
    project_id: int
    shooting_day_id: int
    day_number: int
    shoot_date: str
    general_call_time: str
    location_name: str
    location_address: str
    parking_info: str
    weather_placeholder: str
    nearest_hospital: str
    scenes_summary: Optional[List[Dict[str, Any]]] = []
    cast_calls: Optional[List[Dict[str, Any]]] = []
    crew_calls: Optional[List[Dict[str, Any]]] = []
    equipment_notes: Optional[str] = None
    props_costumes_notes: Optional[str] = None
    special_instructions: Optional[str] = None
    meal_break: str
    emergency_contact: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CallSheetUpdate(BaseModel):
    general_call_time: Optional[str] = None
    location_address: Optional[str] = None
    parking_info: Optional[str] = None
    weather_placeholder: Optional[str] = None
    special_instructions: Optional[str] = None
    emergency_contact: Optional[str] = None
