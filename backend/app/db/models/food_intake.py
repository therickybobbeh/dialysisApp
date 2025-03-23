from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class FoodIntake(Base):
    __tablename__ = "food_intake"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_name = Column(String, nullable=False)
    protein_grams = Column(Float, nullable=False)
    meal_time = Column(DateTime, default=datetime.utcnow)

    #  Keep only **ONE** relationship to avoid conflict
    patient = relationship("User", back_populates="food_intakes", overlaps="food_intakes")
