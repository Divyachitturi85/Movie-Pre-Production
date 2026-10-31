import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    currency = Column(String(10), default="INR")
    
    # Financial totals
    subtotal = Column(Float, default=0.0)
    contingency_rate = Column(Float, default=0.10)  # 10%
    contingency_amount = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.08)  # 8%
    tax_amount = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    
    status = Column(String(50), default="DRAFT")
    disclaimer = Column(String(255), default="Illustrative planning estimates — user configurable.")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="budget")
    items = relationship("BudgetItem", back_populates="budget", cascade="all, delete-orphan")
