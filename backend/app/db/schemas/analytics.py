from pydantic import BaseModel
from datetime import date
from typing import Optional

class DialysisAnalyticsResponse(BaseModel):
    date: date
    avg_pre_weight: Optional[float] = None
    avg_post_weight: Optional[float] = None
    avg_pre_systolic: Optional[float] = None
    avg_pre_diastolic: Optional[float] = None
    avg_post_systolic: Optional[float] = None
    avg_post_diastolic: Optional[float] = None
    avg_effluent: Optional[float] = None

    class Config:
        from_attributes = True  #  Ensures compatibility with ORM models
