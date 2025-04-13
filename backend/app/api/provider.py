from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.schemas.dialysis import DialysisSessionCreate, DialysisSessionResponse
from app.db.schemas.user import UserResponse, ProviderPatientsResponse
from app.db.session import get_db
from app.db.models.dialysis import DialysisSession
from app.core.security import get_current_user
from app.db.models.user import User
import logging

from scripts.populate_db import protein

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/provider", tags=["Provider"])

@router.get("/patients", response_model=List[dict])
def get_provider_patients(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Fetch patients assigned to the provider along with their dialysis information.
    """
    if user.role != "provider":
        raise HTTPException(status_code=403, detail="Access denied")
    if not user.patients:
        return []

    # Query patients assigned to the provider
    patients = db.query(User).filter(User.id.in_(user.patients)).all()

    # Build the response with patient details and dialysis information
    patients_response = []
    for patient in patients:
        # Fetch dialysis sessions for the patient
        dialysis_sessions = db.query(DialysisSession).filter(
            DialysisSession.patient_id == patient.id
        ).order_by(DialysisSession.session_date.desc()).all()

        # Add patient details and dialysis information to the response
        patient_data = {
            "id": patient.id,
            "name": patient.name,
            "email": patient.email,
            "role": patient.role,
            "dialysis_sessions": [
                {
                    "id": session.id,
                    "session_type": session.session_type,
                    "session_date": session.session_date,
                    "weight": session.weight,
                    "systolic": session.systolic,
                    "diastolic": session.diastolic,
                    "protein": session.protein,
                }
                for session in dialysis_sessions
            ],
        }
        patients_response.append(patient_data)
    return patients_response

@router.get("/patients/{patient_id}/dialysis", response_model=List[DialysisSessionResponse])
def get_patient_dialysis_info(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Fetch dialysis information for a specific patient assigned to the provider.
    """
    if user.role != "provider":
        raise HTTPException(status_code=403, detail="Access denied")

    # Ensure the patient is in the provider's `patients` list
    if patient_id not in user.patients:
        raise HTTPException(status_code=403, detail="Access denied")

    # Fetch dialysis sessions for the selected patient
    dialysis_sessions = db.query(DialysisSession).filter(DialysisSession.patient_id == patient_id).all()
    return [DialysisSessionResponse.from_orm(session) for session in dialysis_sessions]


@router.post("/patients/{patient_id}/dialysis", response_model=DialysisSessionResponse)
def create_dialysis_session(
    patient_id: int,
    session_data: DialysisSessionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create or update a dialysis session for a specific patient assigned to the provider.
    """
    if user.role != "provider":
        raise HTTPException(status_code=403, detail="Access denied")

    # Ensure the patient is in the provider's `patients` list
    if patient_id not in user.patients:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        # Check if session_id exists in the request
        if session_data.session_id:
            existing_session = db.query(DialysisSession).filter(
                DialysisSession.session_id == session_data.session_id,
                DialysisSession.patient_id == patient_id
            ).first()

            if existing_session:
                existing_session.session_type = session_data.session_type
                existing_session.weight = session_data.weight
                existing_session.diastolic = session_data.diastolic
                existing_session.systolic = session_data.systolic
                existing_session.effluent_volume = session_data.effluent_volume
                existing_session.session_date = session_data.session_date
                existing_session.session_duration = session_data.session_duration
                existing_session.protein = session_data.protein

                db.commit()
                db.refresh(existing_session)
                return DialysisSessionResponse.from_orm(existing_session)
        else:
            # Fetch the last session ID for the patient
            last_session = db.query(DialysisSession).filter(
                DialysisSession.patient_id == patient_id
            ).order_by(DialysisSession.session_date.desc()).first()

            session_data.session_id = last_session.session_id + 1 if last_session else 1

        # Create a new dialysis session
        new_session = DialysisSession(
            session_type=session_data.session_type,
            session_id=session_data.session_id,
            patient_id=patient_id,
            weight=session_data.weight,
            diastolic=session_data.diastolic,
            systolic=session_data.systolic,
            effluent_volume=session_data.effluent_volume,
            session_date=session_data.session_date,
            session_duration=session_data.session_duration,
            protein=session_data.protein
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return DialysisSessionResponse.from_orm(new_session)

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating or updating dialysis session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create or update dialysis session")