import datetime
from typing import Optional
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
    scene = relationship("Scene", back_populates="scheduled_scenes", lazy="joined")

    @property
    def scene_number(self) -> Optional[int]:
        if self.scene:
            return self.scene.scene_number
        return None

    @property
    def first_line(self) -> Optional[str]:
        """Returns the first non-empty line of the scene from raw_content, heading, or action_text."""
        if self.scene:
            if self.scene.raw_content:
                lines = [line.strip() for line in self.scene.raw_content.split('\n') if line.strip()]
                if lines:
                    return lines[0]
            if self.scene.heading and self.scene.heading.strip():
                return self.scene.heading.strip()
            if self.scene.action_text:
                lines = [line.strip() for line in self.scene.action_text.split('\n') if line.strip()]
                if lines:
                    return lines[0]
        return None

    @property
    def heading(self) -> Optional[str]:
        """User requested the first line of the scene in the slugline/heading column."""
        return self.first_line or (self.scene.heading.strip() if self.scene and self.scene.heading else None)

    @property
    def interior_exterior(self) -> Optional[str]:
        if self.scene:
            return self.scene.interior_exterior
        return None

    @property
    def time_of_day(self) -> Optional[str]:
        if self.scene:
            return self.scene.time_of_day
        return None

    @property
    def pages(self) -> Optional[float]:
        if self.scene:
            return self.scene.estimated_pages
        return None

    @property
    def complexity_level(self) -> Optional[str]:
        if self.scene:
            return self.scene.complexity_level or "LOW"
        return "LOW"
