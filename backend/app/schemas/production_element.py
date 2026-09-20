from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ProductionElementCreate(BaseModel):
    category: str
    name: str
    description: Optional[str] = None
    quantity: int = 1
    scene_id: Optional[int] = None
    confidence: float = 1.0
    extraction_source: str = "USER_ADDED"

class ProductionElementResponse(BaseModel):
    id: int
    project_id: int
    scene_id: Optional[int] = None
    category: str
    name: str
    description: Optional[str] = None
    quantity: int
    confidence: float
    extraction_source: str
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
