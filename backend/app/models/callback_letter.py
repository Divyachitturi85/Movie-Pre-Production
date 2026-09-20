import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class CallbackLetter(Base):
    __tablename__ = "callback_letters"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="SET NULL"), nullable=True)
    
    actor_name = Column(String(150), nullable=False)
    actor_email = Column(String(150), nullable=True)
    character_name = Column(String(150), nullable=False)
    role_type = Column(String(50), default="LEAD")
    
    callback_date = Column(String(50), default="Next Monday")
    callback_time = Column(String(50), default="10:00 AM EST")
    location = Column(String(255), default="Casting Studio Room 3B / Virtual via Zoom")
    sides_reference = Column(String(255), default="Scenes 2 & 4 (Attached Sides)")
    what_to_prepare = Column(Text, default="Please prepare sides memorized. Be prepared for cold read adjustments with Director.")
    contact_person = Column(String(100), default="Casting Director: Sarah Jenkins")
    contact_email = Column(String(100), default="casting@productionhouse.com")
    contact_phone = Column(String(50), default="+1 (555) 012-3456")
    special_instructions = Column(Text, nullable=True)
    
    letter_body = Column(Text, nullable=False)
    status = Column(String(50), default="GENERATED")  # GENERATED, SENT, CONFIRMED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="callback_letters")
    character = relationship("Character", back_populates="callback_letters")
