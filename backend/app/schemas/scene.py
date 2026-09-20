from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ProductionElementBrief(BaseModel):
    id: int
    category: str
    name: str
    quantity: int
    confidence: float
    extraction_source: str
    model_config = ConfigDict(from_attributes=True)

class SceneResponse(BaseModel):
    id: int
    project_id: int
    scene_number: int
    heading: str
    interior_exterior: str
    location_name: str
    time_of_day: str
    page_start: float
    page_end: float
    estimated_pages: float
    estimated_duration_minutes: int
    raw_content: Optional[str] = None
    action_text: Optional[str] = None
    dialogue_count: int
    complexity_score: float
    complexity_level: str
    complexity_factors: Optional[Dict[str, Any]] = None
    sequence_order: int
    notes: Optional[str] = None
    production_elements: Optional[List[ProductionElementBrief]] = None

    model_config = ConfigDict(from_attributes=True)
