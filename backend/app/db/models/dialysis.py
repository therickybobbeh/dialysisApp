from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class DialysisSession(Base):
    __tablename__ = "dialysis_sessions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_type = Column(String, nullable=False)
    session_id: int = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    diastolic = Column(Integer, nullable=False)
    systolic = Column(Integer, nullable=False)
    effluent_volume = Column(Float, nullable=False)
    session_date = Column(DateTime, nullable=False)
    session_duration = Column(String, nullable=True)
    protein = Column(Float, nullable=False)
    # Use lazy string reference instead of direct import
    patient = relationship("User", back_populates="dialysis_sessions")

# IMPORT AT THE END TO AVOID CIRCULAR DEPENDENCY
from app.db.models.user import User
