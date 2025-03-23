from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class DialysisSession(Base):
    __tablename__ = "dialysis_sessions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    pre_systolic = Column(Integer, nullable=False)
    pre_diastolic = Column(Integer, nullable=False)
    post_systolic = Column(Integer, nullable=False)
    post_diastolic = Column(Integer, nullable=False)

    pre_weight = Column(Float, nullable=False)
    post_weight = Column(Float, nullable=False)
    effluent_volume = Column(Float, nullable=False)
    session_date = Column(DateTime, nullable=False)

    #  Use lazy string reference instead of direct import
    patient = relationship("User", back_populates="dialysis_sessions")

#  IMPORT AT THE END TO AVOID CIRCULAR DEPENDENCY
from app.db.models.user import User
