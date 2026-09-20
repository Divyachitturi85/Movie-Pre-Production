from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ScriptResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    file_size_bytes: int
    page_count: int
    extraction_method: str
    ocr_confidence: float
    raw_text: Optional[str] = None
    cleaned_text: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ScriptParseRequest(BaseModel):
    raw_text: Optional[str] = None
