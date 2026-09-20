import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class AIExplainabilityRecord(Base):
    __tablename__ = "ai_explainability_records"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    stage = Column(String(50), nullable=False)  # OCR, SCRIPT_PARSING, NER_CHARACTER, NER_LOCATION, NER_PROPS, COMPLEXITY, ORTOOLS_SCHEDULING, BUDGET
    target_entity = Column(String(100), nullable=True)  # e.g. "Scene 4", "Character: Marcus", "Location: Warehouse"
    
    input_data = Column(Text, nullable=True)
    ai_method = Column(String(150), nullable=False)     # e.g. "Hugging Face BERT-NER + spaCy Linguistic + Heuristics"
    output_detected = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    fallback_used = Column(Boolean, default=False)
    fallback_reason = Column(String(255), nullable=True)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="explainability_records")
