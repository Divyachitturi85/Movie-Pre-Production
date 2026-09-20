import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProductionElement(Base):
    __tablename__ = "production_elements"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    scene_id = Column(Integer, ForeignKey("scenes.id", ondelete="CASCADE"), nullable=True)
    
    # Category: PROP, COSTUME, VEHICLE, EQUIPMENT, VFX, SFX, ANIMAL, WEAPON, MAKEUP, SET_DRESSING, SOUND, CAMERA
    category = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, default=1)
    
    confidence = Column(Float, default=0.85)
    extraction_source = Column(String(100), default="HEURISTIC_RULE")  # SPACY, HUGGING_FACE, HEURISTIC_RULE, USER_ADDED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="production_elements")
    scene = relationship("Scene", back_populates="production_elements")
