import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from app.db.session import get_db
from app.db.models.dialysis import DialysisSession
from app.db.models.food_intake import FoodIntake
from app.db.schemas.food_intake import FoodIntakeCreate, FoodIntakeResponse
from app.core.security import get_current_user
from app.db.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patient", tags=["Patient"])

#  **Track daily meals**
@router.post("/meals", response_model=FoodIntakeResponse)
def log_meal(
    meal_data: FoodIntakeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Allows patients to log meals and track protein intake."""
    if user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can log meals")

    try:
        new_meal = FoodIntake(
            patient_id=user.id,
            food_name=meal_data.food_name,
            protein_grams=meal_data.protein_grams,
            meal_time=meal_data.meal_time or datetime.utcnow()
        )

        db.add(new_meal)
        db.commit()
        db.refresh(new_meal)

        logger.info(f"Meal logged for patient {user.id}: {meal_data.food_name} ({meal_data.protein_grams}g protein)")
        return new_meal

    except Exception as e:
        db.rollback()
        logger.error(f"Error logging meal: {e}")
        raise HTTPException(status_code=500, detail="Failed to log meal")

#  **Patient Dashboard: Show Dialysis & Meal Trends**
@router.get("/dashboard")
def patient_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Provides a summary of dialysis & meal trends for the patient."""
    if user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can view this dashboard")

    try:
        #  Fetch last 30 days of dialysis sessions
        last_30_days = datetime.utcnow() - timedelta(days=30)
        sessions = db.query(DialysisSession).filter(
            DialysisSession.patient_id == user.id,
            DialysisSession.session_date >= last_30_days
        ).order_by(DialysisSession.session_date.desc()).all()

        #  Fetch last 30 days of meals
        meals = db.query(FoodIntake).filter(
            FoodIntake.patient_id == user.id,
            FoodIntake.meal_time >= last_30_days
        ).order_by(FoodIntake.meal_time.desc()).all()

        #  Compute average protein intake
        total_protein = sum(meal.protein_grams for meal in meals)
        avg_protein = total_protein / len(meals) if meals else 0

        #  Compute weight & BP trends // todo: need to abstract out to get pre and post
        weight_trend = [(s.session_date, s.post_weight) for s in sessions]
        bp_trend = [(s.session_date, s.post_systolic, s.post_diastolic) for s in sessions]

        #  Detect negative trends
        alerts = []
        if avg_protein < 50:
            alerts.append("Low protein intake detected. Consult your provider.")
        if len(sessions) < 5:
            alerts.append("Dialysis session count low in last 30 days.")

        return {
            "patient_id": user.id,
            "recent_weight_trend": weight_trend,
            "recent_bp_trend": bp_trend,
            "avg_protein_intake": avg_protein,
            "alerts": alerts
        }

    except Exception as e:
        logger.error(f"Error retrieving patient dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve patient dashboard")


