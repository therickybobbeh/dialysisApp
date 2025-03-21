from pydantic import BaseModel
from datetime import datetime

class FoodIntakeCreate(BaseModel):
    food_name: str
    protein_grams: float
    meal_time: datetime | None = None  # Optional field

class FoodIntakeResponse(FoodIntakeCreate):
    id: int
    patient_id: int

    class Config:
        from_attributes = True
