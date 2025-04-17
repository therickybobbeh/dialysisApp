import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict

from app.db.session import get_db
from app.db.models.dialysis import DialysisSession
from app.db.models.user import User
from app.core.security import get_current_user
from app.db.schemas.analytics import DialysisAnalyticsResponse

logger = logging.getLogger(__name__)

#  Fix Prefix to Avoid Route Conflicts
router = APIRouter(prefix="/analytics", tags=["Dialysis Analytics"])


# todo: we need to map the pre and post sessions. the db changed a bit
@router.get("/analytics")
def dialysis_analytics(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
) -> List[Dict]:
    """Returns aggregated dialysis data trends with risk alerts for the logged-in patient"""

    try:
        #  Aggregate patient dialysis trends
        # TODO: Fix this query to get the 2 sessions, combine and then calculate the averages
        # can use the pre and post fields
        query = None;
        # query = db.query(
        #     DialysisSession.session_date,
        #     func.avg(DialysisSession.pre_weight).label("avg_pre_weight"),
        #     func.avg(DialysisSession.post_weight).label("avg_post_weight"),
        #     func.avg(DialysisSession.pre_systolic).label("avg_pre_systolic"),
        #     func.avg(DialysisSession.pre_diastolic).label("avg_pre_diastolic"),
        #     func.avg(DialysisSession.post_systolic).label("avg_post_systolic"),
        #     func.avg(DialysisSession.post_diastolic).label("avg_post_diastolic"),
        #     func.avg(DialysisSession.effluent_volume).label("avg_effluent")
        # ).filter(DialysisSession.patient_id == user.id)

        #  Apply date filters if provided
        if start_date:
            query = query.filter(DialysisSession.session_date >= start_date)
        if end_date:
            query = query.filter(DialysisSession.session_date <= end_date)

        query = query.group_by(DialysisSession.session_date).order_by(DialysisSession.session_date.asc())
        trends = query.all()

        #  Process data and add risk alerts
        result = []
        for row in trends:
            alert_messages = []

            #  **Risk Conditions**
            if row.avg_pre_systolic > 140 or row.avg_post_systolic > 140:
                alert_messages.append("High blood pressure detected. Contact provider.")

            if row.avg_post_weight - row.avg_pre_weight > 2.0:
                alert_messages.append("Significant weight increase detected. Monitor fluid retention.")

            if row.avg_effluent < 1.5:
                alert_messages.append("Low effluent volume. May indicate insufficient dialysis.")

            result.append({
                "date": row.session_date.strftime("%Y-%m-%d"),
                "avg_pre_weight": row.avg_pre_weight,
                "avg_post_weight": row.avg_post_weight,
                "avg_pre_systolic": row.avg_pre_systolic,
                "avg_pre_diastolic": row.avg_pre_diastolic,
                "avg_post_systolic": row.avg_post_systolic,
                "avg_post_diastolic": row.avg_post_diastolic,
                "avg_effluent": row.avg_effluent,
                "alerts": alert_messages  # Include risk alerts in response
            })

        return result

    except Exception as e:
        logger.error(f"Error retrieving dialysis analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")


@router.get("/notifications")
def get_user_notifications(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict:
    """Retrieve notifications for the logged-in user or a specific user if the role is provider."""
    try:
        if user.role == "patient":
            target_user_id = user.id
        elif user.role == "provider":
            if not user_id:
                raise HTTPException(status_code=400, detail="User ID is required for providers")
            target_user_id = user_id
        else:
            raise HTTPException(status_code=403, detail="Access denied")

        # Query the target user's notifications
        target_user = db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        notifications = target_user.notifications or {}
        return notifications

    except Exception as e:
        logger.error(f"Error retrieving notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve notifications")


@router.put("/notifications")
def update_user_notifications(
    notifications: Dict,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Dict:
    """Update notifications for the logged-in user or a specific user if the role is provider."""
    try:
        if user.role == "patient":
            target_user_id = user.id
        elif user.role == "provider":
            if not user_id:
                raise HTTPException(status_code=400, detail="User ID is required for providers")
            target_user_id = user_id
        else:
            raise HTTPException(status_code=403, detail="Access denied")

        # Query the target user
        target_user = db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update the notifications field
        target_user.notifications = notifications
        db.commit()
        return {"message": "Notifications updated successfully"}

    except Exception as e:
        logger.error(f"Error updating notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notifications")