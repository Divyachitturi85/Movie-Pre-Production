import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Scene(Base):
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    heading = Column(String(255), nullable=False)
    interior_exterior = Column(String(20), default="INT")  # INT, EXT, INT/EXT
    location_name = Column(String(255), nullable=False, default="UNKNOWN SET")
    time_of_day = Column(String(50), default="DAY")  # DAY, NIGHT, DUSK, DAWN, EVENING, CONTINUOUS
    
    # Page and duration
    page_start = Column(Float, default=1.0)
    page_end = Column(Float, default=1.0)
    estimated_pages = Column(Float, default=0.5)  # in pages or 1/8ths
    estimated_duration_minutes = Column(Integer, default=60)  # shooting minutes
    
    # Content
    raw_content = Column(Text, nullable=True)
    action_text = Column(Text, nullable=True)
    dialogue_count = Column(Integer, default=0)
    
    # Complexity
    complexity_score = Column(Float, default=1.0)
    complexity_level = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH, VERY HIGH
    complexity_factors = Column(JSON, default=dict)
    
    sequence_order = Column(Integer, default=1)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="scenes")
    production_elements = relationship("ProductionElement", back_populates="scene", cascade="all, delete-orphan")
    scheduled_scenes = relationship("ScheduledScene", back_populates="scene", cascade="all, delete-orphan")
