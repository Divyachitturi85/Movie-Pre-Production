import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class CallSheet(Base):
    __tablename__ = "call_sheets"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    shooting_day_id = Column(Integer, ForeignKey("shooting_days.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    day_number = Column(Integer, nullable=False)
    shoot_date = Column(String(50), nullable=False)
    general_call_time = Column(String(20), default="07:00 AM")
    location_name = Column(String(255), nullable=False)
    location_address = Column(String(255), default="Stage 4 / Practical Location")
    parking_info = Column(String(255), default="Lot B - Crew Parking passes required")
    weather_placeholder = Column(String(255), default="Sunny, 72°F / 22°C, Low humidity")
    nearest_hospital = Column(String(255), default="City Central Emergency Hospital, 911 / (555) 019-2834")
    
    scenes_summary = Column(JSON, default=list)  # list of scenes with slugline, cast, pages
    cast_calls = Column(JSON, default=list)      # list of actors, characters, pickup, h/mu, on-set
    crew_calls = Column(JSON, default=list)      # list of departments with call times
    equipment_notes = Column(Text, nullable=True)
    props_costumes_notes = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)
    meal_break = Column(String(100), default="13:00 (45 minutes courtesy lunch)")
    emergency_contact = Column(String(255), default="1st AD: Jane Doe (555-0199) | Production Mgr: Bob Smith (555-0198)")
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="call_sheets")
    shooting_day = relationship("ShootingDay", back_populates="call_sheet")
