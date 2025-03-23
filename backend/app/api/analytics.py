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
router = APIRouter(prefix="/dialysis", tags=["Dialysis Analytics"])

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
        query = db.query(
            DialysisSession.session_date,
            func.avg(DialysisSession.pre_weight).label("avg_pre_weight"),
            func.avg(DialysisSession.post_weight).label("avg_post_weight"),
            func.avg(DialysisSession.pre_systolic).label("avg_pre_systolic"),
            func.avg(DialysisSession.pre_diastolic).label("avg_pre_diastolic"),
            func.avg(DialysisSession.post_systolic).label("avg_post_systolic"),
            func.avg(DialysisSession.post_diastolic).label("avg_post_diastolic"),
            func.avg(DialysisSession.effluent_volume).label("avg_effluent")
        ).filter(DialysisSession.patient_id == user.id)

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
