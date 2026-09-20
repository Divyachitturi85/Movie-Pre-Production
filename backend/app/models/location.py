import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    interior_exterior = Column(String(20), default="INT")  # INT, EXT, INT/EXT
    day_night = Column(String(50), default="DAY")
    scene_count = Column(Integer, default=0)
    required_days = Column(Integer, default=1)
    company_move_required = Column(Boolean, default=False)
    estimated_cost = Column(Float, default=1500.0)
    address_or_description = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    scene_ids = Column(JSON, default=list)  # list of scene numbers

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="locations")
