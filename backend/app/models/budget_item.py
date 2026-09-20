import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class BudgetItem(Base):
    __tablename__ = "budget_items"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    
    # Category: ABOVE_THE_LINE, BELOW_THE_LINE, POST_PRODUCTION, OTHER
    category = Column(String(50), nullable=False, default="BELOW_THE_LINE")
    # Department: Cast, Camera, Lighting, Sound, Art, Costume, Makeup, Transportation, Location, Catering, VFX, etc.
    department = Column(String(100), nullable=False)
    account_code = Column(String(20), nullable=True)  # e.g. "1100", "2200"
    description = Column(String(255), nullable=False)
    
    quantity = Column(Float, default=1.0)
    unit = Column(String(50), default="Days")  # Days, Weeks, Flat, Hours, Units
    unit_rate = Column(Float, default=0.0)
    days_count = Column(Float, default=1.0)
    subtotal = Column(Float, default=0.0)
    
    is_custom = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    budget = relationship("Budget", back_populates="items")
