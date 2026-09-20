from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CallbackLetterCreate(BaseModel):
    character_id: Optional[int] = None
    actor_name: str
    actor_email: Optional[str] = None
    character_name: str
    role_type: Optional[str] = "LEAD"
    callback_date: Optional[str] = "Next Monday"
    callback_time: Optional[str] = "10:00 AM EST"
    location: Optional[str] = "Studio 3B / Virtual Zoom"
    sides_reference: Optional[str] = "Scenes 2 & 4"
    what_to_prepare: Optional[str] = "Please prepare sides memorized."
    contact_person: Optional[str] = "Sarah Jenkins (Casting Director)"
    contact_email: Optional[str] = "casting@auroraproductions.com"
    contact_phone: Optional[str] = "+1 (555) 012-3456"
    special_instructions: Optional[str] = None

class CallbackLetterResponse(BaseModel):
    id: int
    project_id: int
    character_id: Optional[int] = None
    actor_name: str
    actor_email: Optional[str] = None
    character_name: str
    role_type: str
    callback_date: str
    callback_time: str
    location: str
    sides_reference: str
    what_to_prepare: str
    contact_person: str
    contact_email: str
    contact_phone: str
    special_instructions: Optional[str] = None
    letter_body: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
