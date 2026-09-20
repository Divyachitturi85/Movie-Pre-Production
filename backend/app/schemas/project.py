from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ProjectBase(BaseModel):
    name: str = "Untitled Production"
    description: Optional[str] = None
    genre: Optional[str] = "Sci-Fi / Thriller"
    director: Optional[str] = "TBD"
    producer: Optional[str] = "TBD"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    director: Optional[str] = None
    producer: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    status: str
    current_stage: str
    created_at: datetime
    updated_at: datetime
    
    # Counts
    scene_count: Optional[int] = 0
    character_count: Optional[int] = 0
    location_count: Optional[int] = 0
    total_shooting_days: Optional[int] = 0
    estimated_budget: Optional[float] = 0.0

    model_config = ConfigDict(from_attributes=True)
