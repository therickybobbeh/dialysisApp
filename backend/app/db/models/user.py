from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="patient")

    #  Relationships
    dialysis_sessions = relationship("DialysisSession", back_populates="patient", cascade="all, delete-orphan")
    food_intakes = relationship("FoodIntake", back_populates="patient", cascade="all, delete-orphan", overlaps="food_intakes")

#  IMPORT AT THE END TO AVOID CIRCULAR DEPENDENCY
from app.db.models.dialysis import DialysisSession
from app.db.models.food_intake import FoodIntake
