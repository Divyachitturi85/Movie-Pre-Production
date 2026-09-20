from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CharacterResponse(BaseModel):
    id: int
    project_id: int
    name: str
    role: str
    scene_count: int
    dialogue_count: int
    estimated_screen_time_minutes: float
    required_shooting_days: int
    costume_requirements: Optional[str] = None
    makeup_requirements: Optional[str] = None
    notes: Optional[str] = None
    scene_ids: Optional[List[int]] = []

    model_config = ConfigDict(from_attributes=True)

class CharacterUpdate(BaseModel):
    role: Optional[str] = None
    costume_requirements: Optional[str] = None
    makeup_requirements: Optional[str] = None
    notes: Optional[str] = None
