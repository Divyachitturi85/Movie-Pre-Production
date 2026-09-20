import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ShootingDay(Base):
    __tablename__ = "shooting_days"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    day_number = Column(Integer, nullable=False)
    shoot_date = Column(String(50), nullable=True)  # e.g. "Day 1 - Monday"
    call_time = Column(String(20), default="07:00 AM")
    wrap_time = Column(String(20), default="06:30 PM")
    meal_break_time = Column(String(20), default="01:00 PM (45 mins)")
    total_shooting_hours = Column(Float, default=9.5)
    company_moves_count = Column(Integer, default=0)
    primary_location = Column(String(255), nullable=True)
    
    # Summary cached info
    cast_ids = Column(JSON, default=list)
    equipment_ids = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    schedule = relationship("Schedule", back_populates="shooting_days")
    scheduled_scenes = relationship("ScheduledScene", back_populates="shooting_day", cascade="all, delete-orphan", order_by="ScheduledScene.sequence_order")
    call_sheet = relationship("CallSheet", back_populates="shooting_day", uselist=False, cascade="all, delete-orphan")
