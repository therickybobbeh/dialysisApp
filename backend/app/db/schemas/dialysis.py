from pydantic import BaseModel, Field
from datetime import datetime

class DialysisSessionCreate(BaseModel):
    patient_id: int = Field(..., description="ID of the patient")  #  Added patient_id
    pre_weight: float = Field(..., description="Pre-dialysis weight in kg")
    post_weight: float = Field(..., description="Post-dialysis weight in kg")
    
    pre_systolic: int = Field(..., description="Pre-dialysis systolic blood pressure (mmHg)")
    pre_diastolic: int = Field(..., description="Pre-dialysis diastolic blood pressure (mmHg)")
    post_systolic: int = Field(..., description="Post-dialysis systolic blood pressure (mmHg)")
    post_diastolic: int = Field(..., description="Post-dialysis diastolic blood pressure (mmHg)")
    
    effluent_volume: float = Field(..., description="Volume of effluent removed in liters")
    session_date: datetime = Field(..., description="Date and time of the dialysis session")  #  Added session_date

class DialysisSessionResponse(DialysisSessionCreate):
    id: int

    class Config:
        from_attributes = True  # Use `from_attributes` instead of `orm_mode` (Pydantic V2)
