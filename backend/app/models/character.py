import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    role = Column(String(50), default="SUPPORTING")  # LEAD, SUPPORTING, MINOR, EXTRA
    scene_count = Column(Integer, default=0)
    dialogue_count = Column(Integer, default=0)
    estimated_screen_time_minutes = Column(Float, default=0.0)
    required_shooting_days = Column(Integer, default=1)
    
    # Requirements
    costume_requirements = Column(Text, nullable=True)
    makeup_requirements = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    scene_ids = Column(JSON, default=list)  # list of scene numbers
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="characters")
    callback_letters = relationship("CallbackLetter", back_populates="character", cascade="all, delete-orphan")
