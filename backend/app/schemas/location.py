from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class LocationResponse(BaseModel):
    id: int
    project_id: int
    name: str
    interior_exterior: str
    day_night: str
    scene_count: int
    required_days: int
    company_move_required: bool
    estimated_cost: float
    address_or_description: Optional[str] = None
    notes: Optional[str] = None
    scene_ids: Optional[List[int]] = []

    model_config = ConfigDict(from_attributes=True)
