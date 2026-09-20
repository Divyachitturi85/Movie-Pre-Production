import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), default="Primary Production Schedule")
    total_days = Column(Integer, default=0)
    total_shooting_hours = Column(Float, default=0.0)
    total_company_moves = Column(Integer, default=0)
    optimization_status = Column(String(50), default="OPTIMAL")  # OPTIMAL, FEASIBLE, HEURISTIC
    solver_time_seconds = Column(Float, default=0.0)
    objective_value = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="schedules")
    shooting_days = relationship("ShootingDay", back_populates="schedule", cascade="all, delete-orphan", order_by="ShootingDay.day_number")
