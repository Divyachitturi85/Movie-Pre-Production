import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, default="Untitled Production")
    description = Column(Text, nullable=True)
    genre = Column(String(100), nullable=True, default="Drama / Sci-Fi")
    director = Column(String(100), nullable=True, default="TBD")
    producer = Column(String(100), nullable=True, default="TBD")
    status = Column(String(50), default="CREATED")  # CREATED, PARSED, ANALYZED, SCHEDULED, BUDGETED, COMPLETED
    current_stage = Column(String(50), default="INIT")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    script = relationship("Script", back_populates="project", uselist=False, cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan", order_by="Scene.scene_number")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="project", cascade="all, delete-orphan")
    production_elements = relationship("ProductionElement", back_populates="project", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="project", cascade="all, delete-orphan")
    budget = relationship("Budget", back_populates="project", uselist=False, cascade="all, delete-orphan")
    call_sheets = relationship("CallSheet", back_populates="project", cascade="all, delete-orphan")
    callback_letters = relationship("CallbackLetter", back_populates="project", cascade="all, delete-orphan")
    explainability_records = relationship("AIExplainabilityRecord", back_populates="project", cascade="all, delete-orphan")
