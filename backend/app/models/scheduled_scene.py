import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ScheduledScene(Base):
    __tablename__ = "scheduled_scenes"

    id = Column(Integer, primary_key=True, index=True)
    shooting_day_id = Column(Integer, ForeignKey("shooting_days.id", ondelete="CASCADE"), nullable=False)
    scene_id = Column(Integer, ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False)
    sequence_order = Column(Integer, default=1)
    
    estimated_start_time = Column(String(20), default="08:00 AM")
    estimated_duration_minutes = Column(Integer, default=60)
    setup_time_minutes = Column(Integer, default=30)
    location_name = Column(String(255), nullable=True)
    company_move_before = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    shooting_day = relationship("ShootingDay", back_populates="scheduled_scenes")
    scene = relationship("Scene", back_populates="scheduled_scenes")
