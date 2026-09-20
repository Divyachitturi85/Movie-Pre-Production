from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ExplainabilityResponse(BaseModel):
    id: int
    project_id: int
    stage: str
    target_entity: Optional[str] = None
    input_data: Optional[str] = None
    ai_method: str
    output_detected: Optional[str] = None
    confidence: float
    fallback_used: bool
    fallback_reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
