import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Tuple, List

from app.db.session import get_db
from app.db.models.dialysis import DialysisSession
from app.db.models.user import User
from app.core.security import get_current_user
from app.db.schemas.analytics import DialysisAnalyticsResponse

logger = logging.getLogger(__name__)

#  Fix Prefix to Avoid Route Conflicts
router = APIRouter(prefix="/analytics", tags=["Dialysis Analytics"])

# Blood Pressure Reference Data - Based on 90th and 50th percentiles by age, gender, and height
# This is a simplified version. In a real application, this would be more comprehensive
# Reference: https://kidneyfoundation.cachefly.net/professionals/KDOQI/guidelines_bp/guide_13.htm
# This simplified implementation includes 3 height percentiles (5th, 50th, 95th) for accurate BP assessment
# Height percentile definitions: "short" (5th), "medium" (50th), "tall" (95th)
BP_REFERENCE = {
    "male": {
        # Age ranges with height percentiles: (high_systolic, high_diastolic, low_systolic, low_diastolic)
        # High is 90th percentile, Low is 50th percentile
        "1-3": {
            "short": {"90th": (106, 70), "50th": (91, 52)},
            "medium": {"90th": (110, 74), "50th": (95, 55)},
            "tall": {"90th": (114, 76), "50th": (99, 57)}
        },
        "4-6": {
            "short": {"90th": (110, 74), "50th": (97, 57)},
            "medium": {"90th": (114, 76), "50th": (100, 60)},
            "tall": {"90th": (118, 78), "50th": (104, 63)}
        },
        "7-10": {
            "short": {"90th": (114, 76), "50th": (102, 62)},
            "medium": {"90th": (118, 78), "50th": (105, 65)},
            "tall": {"90th": (122, 80), "50th": (109, 68)}
        },
        "11-14": {
            "short": {"90th": (118, 78), "50th": (107, 63)},
            "medium": {"90th": (122, 80), "50th": (110, 65)},
            "tall": {"90th": (126, 82), "50th": (114, 67)}
        },
        "15-17": {
            "short": {"90th": (126, 80), "50th": (113, 68)},
            "medium": {"90th": (130, 82), "50th": (115, 70)},
            "tall": {"90th": (134, 84), "50th": (119, 72)}
        }
    },
    "female": {
        "1-3": {
            "short": {"90th": (104, 70), "50th": (91, 52)},
            "medium": {"90th": (108, 72), "50th": (95, 55)},
            "tall": {"90th": (112, 74), "50th": (99, 57)}
        },
        "4-6": {
            "short": {"90th": (108, 72), "50th": (97, 57)},
            "medium": {"90th": (112, 74), "50th": (100, 60)},
            "tall": {"90th": (116, 76), "50th": (104, 63)}
        },
        "7-10": {
            "short": {"90th": (112, 74), "50th": (102, 62)},
            "medium": {"90th": (116, 76), "50th": (105, 65)},
            "tall": {"90th": (120, 78), "50th": (109, 68)}
        },
        "11-14": {
            "short": {"90th": (116, 76), "50th": (107, 63)},
            "medium": {"90th": (120, 78), "50th": (110, 65)},
            "tall": {"90th": (124, 80), "50th": (113, 67)}
        },
        "15-17": {
            "short": {"90th": (120, 78), "50th": (112, 68)},
            "medium": {"90th": (124, 80), "50th": (115, 70)},
            "tall": {"90th": (128, 82), "50th": (118, 72)}
        }
    }
}

# Standard height ranges (cm) by age and gender for percentile calculation
# Values represent 5th, 50th, and 95th percentiles
# Reference: CDC Growth Charts, 2000
# Source: https://www.cdc.gov/growthcharts/cdc-data-files.htm
# Data from: Stature-for-age charts, 2 to 20 years, LMS parameters and
# selected smoothed stature percentiles in centimeters, by sex and age
HEIGHT_REFERENCE = {
    "male": {
        "1-3": [80.0, 91.9, 103.4],    # 5th, 50th, 95th percentiles
        "4-6": [99.9, 112.2, 124.4],
        "7-10": [119.2, 133.3, 147.4],
        "11-14": [142.2, 160.7, 179.0],
        "15-17": [163.3, 176.2, 188.7]
    },
    "female": {
        "1-3": [78.9, 90.7, 102.0],
        "4-6": [99.1, 110.9, 123.1],
        "7-10": [118.2, 132.4, 146.2],
        "11-14": [142.4, 158.0, 172.3],
        "15-17": [154.2, 163.7, 173.6]
    }
}

def determine_height_percentile(height: float, age: int, gender: str) -> str:
    """Determine height percentile category (short, medium, tall) based on height, age, and gender"""
    gender = gender.lower()

    # Determine age range
    if 1 <= age <= 3:
        age_range = "1-3"
    elif 4 <= age <= 6:
        age_range = "4-6"
    elif 7 <= age <= 10:
        age_range = "7-10"
    elif 11 <= age <= 14:
        age_range = "11-14"
    elif age >= 15:
        age_range = "15-17"
    else:
        # For children under 1 year, use the 1-3 range as default
        age_range = "1-3"

    # Get reference heights for this age/gender
    percentiles = HEIGHT_REFERENCE[gender][age_range]

    # Determine percentile category
    if height < percentiles[0]:
        return "short"  # Below 5th percentile
    elif height < percentiles[1]:
        return "short"  # Between 5th and 50th, closer to 5th
    elif height < percentiles[2]:
        return "medium"  # Between 50th and 95th, closer to 50th
    else:
        return "tall"  # Above 95th percentile

def get_bp_reference_values(age: int, gender: str, height: float) -> Dict[str, Tuple[int, int]]:
    """Get blood pressure reference values based on age, gender, and height"""
    gender = gender.lower()

    # Determine age range
    if 1 <= age <= 3:
        age_range = "1-3"
    elif 4 <= age <= 6:
        age_range = "4-6"
    elif 7 <= age <= 10:
        age_range = "7-10"
    elif 11 <= age <= 14:
        age_range = "11-14"
    elif age >= 15:
        age_range = "15-17"
    else:
        # For children under 1 year, use the 1-3 range as default
        age_range = "1-3"

    # Determine height percentile
    height_category = determine_height_percentile(height, age, gender)

    return BP_REFERENCE[gender][age_range][height_category]

def analyze_blood_pressure(pre_systolic, pre_diastolic, post_systolic, post_diastolic, age, gender, height) -> Dict[
    str, bool]:
    bp_ref = get_bp_reference_values(age, gender, height)
    high_systolic, high_diastolic = bp_ref["90th"]
    low_systolic, low_diastolic = bp_ref["50th"]

    return {
        "highBloodPressure": any([
            pre_systolic > high_systolic,
            pre_diastolic > high_diastolic,
            post_systolic > high_systolic,
            post_diastolic > high_diastolic
        ]),
        "lowBloodPressure": any([
            pre_systolic < low_systolic,
            pre_diastolic < low_diastolic,
            post_systolic < low_systolic,
            post_diastolic < low_diastolic
        ])
    }


def analyze_weight(pre_weight: float, post_weight: float, edw: float, uf_volume: float) -> Dict[str, bool]:
    pre_edw_diff_percent = abs((pre_weight - edw) / edw) * 100
    post_edw_diff_percent = abs((post_weight - edw) / edw) * 100
    pre_post_diff_percent = ((post_weight - pre_weight) / pre_weight) * 100

    return {
        "fluidOverloadHigh": pre_edw_diff_percent > 3 or pre_post_diff_percent >= 1,
        "fluidOverloadWatch": post_weight < edw and abs(post_edw_diff_percent) > 2,
        "dialysisGrowthAdjustment": pre_edw_diff_percent > 3
    }

def get_latest_edw(patient_id: int, db: Session) -> float:
    """
    Get the patient's latest Estimated Dry Weight (EDW) from their records.
    First tries to use last recorded post-dialysis weight as proxy for EDW.
    If that's not available, uses the weight from patient's chart as fallback.
    """
    # Try to get the latest post-dialysis session weight
    # Return a default weight if no data is available
    latest_session = db.query(DialysisSession)\
        .filter(DialysisSession.patient_id == patient_id)\
        .order_by(DialysisSession.session_date.desc())\
        .first()
    return latest_session.edw if latest_session else 0.0

# todo: future work could include analyzing uf volume based on patient weight and session time and set alerts if it is, min expected volume or above max expected volume
# todo: we need to map the pre and post sessions. the db changed a bit

@router.get("/notifications")
def get_user_notifications(
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
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

        # Get the target user
        target_user = db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Initialize notification flags
        notifications = {
            "protein": False,
            "effluentVolume": False,
            "lowBloodPressure": False,
            "fluidOverloadHigh": False,
            "highBloodPressure": False,
            "fluidOverloadWatch": False,
            "dialysisGrowthAdjustment": False
        }

        # Get dialysis sessions
        query = db.query(DialysisSession).filter(DialysisSession.patient_id == target_user_id)
        if start_date:
            query = query.filter(DialysisSession.session_date >= start_date)
        if end_date:
            query = query.filter(DialysisSession.session_date <= end_date)
        sessions = query.order_by(DialysisSession.session_date.desc()).all()

        if sessions:
            latest_edw = get_latest_edw(target_user_id, db)
            latest_session = sessions[0]  # Most recent session

            # Blood pressure analysis
            notifications.update(analyze_blood_pressure(
                latest_session.pre_systolic,
                latest_session.pre_diastolic,
                latest_session.post_systolic,
                latest_session.post_diastolic,
                target_user.age,
                target_user.gender,
                target_user.height
            ))

            # Weight analysis
            weight_notifications = analyze_weight(
                latest_session.pre_weight,
                latest_session.post_weight,
                latest_edw,
                latest_session.uf_volume
            )
            notifications.update(weight_notifications)

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