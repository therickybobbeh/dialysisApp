from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DialysisSessionCreate(BaseModel):
    session_type: str = Field(..., description="Type of the session: 'pre' or 'post'")
    session_id: int = Field(..., description="ID of the session")
    patient_id: int = Field(..., description="ID of the patient")
    weight: float = Field(..., description="Weight in kg")
    diastolic: int = Field(..., description="Diastolic blood pressure (mmHg)")
    systolic: int = Field(..., description="Systolic blood pressure (mmHg)")
    effluent_volume: float = Field(..., description="Volume of effluent removed in liters")
    session_date: datetime = Field(..., description="Date and time of the dialysis session")
    session_duration: Optional[str] = Field(None, description="Duration of the session")
    protein: float = Field(..., description="Protein level in the effluent")

class DialysisSessionResponse(DialysisSessionCreate):
    id: int

    class Config:
        from_attributes = True  # Use `from_attributes` instead of `orm_mode` (Pydantic V2)
