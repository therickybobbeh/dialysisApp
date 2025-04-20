from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class DialysisAnalyticsResponse(BaseModel):
    """
    Response model for dialysis session analytics containing averaged measurements.

    All measurements are optional and represent statistical averages of:
    - Pre and post dialysis weight
    - Pre and post dialysis blood pressure (systolic and diastolic)
    - Effluent volume
    """

    date: date = Field(description="Date of the analytics measurements")

    # Weight measurements
    avg_pre_weight: Optional[float] = Field(
        default=None,
        description="Average pre-dialysis weight in kilograms"
    )
    avg_post_weight: Optional[float] = Field(
        default=None,
        description="Average post-dialysis weight in kilograms"
    )

    # Blood pressure measurements - Pre dialysis
    avg_pre_systolic: Optional[float] = Field(
        default=None,
        description="Average pre-dialysis systolic blood pressure in mmHg"
    )
    avg_pre_diastolic: Optional[float] = Field(
        default=None,
        description="Average pre-dialysis diastolic blood pressure in mmHg"
    )

    # Blood pressure measurements - Post dialysis
    avg_post_systolic: Optional[float] = Field(
        default=None,
        description="Average post-dialysis systolic blood pressure in mmHg"
    )
    avg_post_diastolic: Optional[float] = Field(
        default=None,
        description="Average post-dialysis diastolic blood pressure in mmHg"
    )

    # Effluent measurement
    avg_effluent: Optional[float] = Field(
        default=None,
        description="Average effluent volume in milliliters"
    )

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models
