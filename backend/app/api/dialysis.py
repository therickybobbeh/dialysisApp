import logging
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Set, Dict
from datetime import datetime, timedelta
from sqlalchemy.sql import func
from app.db.session import get_db
from app.db.models.dialysis import DialysisSession
from app.db.schemas.dialysis import DialysisSessionCreate, DialysisSessionResponse
from app.core.security import get_current_user
from app.db.models.user import User

logger = logging.getLogger(__name__)

#  Fix Prefix to Avoid Duplicate Routes
router = APIRouter(prefix="/dialysis", tags=["Dialysis"])

#  Maintain active WebSocket connections
active_connections: Set[WebSocket] = set()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection to push real-time updates."""
    await websocket.accept()
    active_connections.add(websocket)
    logger.info(f"New WebSocket connection established ({len(active_connections)} active clients)")

    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.warning(f"WebSocket client disconnected ({len(active_connections)} active clients)")


async def notify_clients(data: dict):
    """Send updates to all connected WebSocket clients."""
    disconnected_clients = []
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except Exception as e:
            logger.error(f"Error sending WebSocket update: {e}")
            disconnected_clients.append(connection)

    #  Remove closed connections
    for conn in disconnected_clients:
        active_connections.remove(conn)


#   Route: `POST /dialysis/sessions`
@router.post("/sessions", response_model=DialysisSessionResponse)
async def log_dialysis_session(
        session_data: DialysisSessionCreate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    """Log a new dialysis session and notify clients."""

    # Check if patient exists
    patient = db.query(User).filter(User.id == session_data.patient_id, User.role == "patient").first()
    if not patient:
        logger.error(f"Patient with ID {session_data.patient_id} does not exist.")
        raise HTTPException(status_code=400, detail="Invalid patient ID: Patient does not exist")

    # Check for duplicate session type on the same day
    existing_session = (
        db.query(DialysisSession)
        .filter(
            DialysisSession.patient_id == session_data.patient_id,
            DialysisSession.session_date >= session_data.session_date.date(),
            DialysisSession.session_type == session_data.session_type
        )
        .first()
    )
    if existing_session:
        logger.warning(
            f"Duplicate {session_data.session_type} session detected for patient {session_data.patient_id} on {session_data.session_date}")
        raise HTTPException(status_code=400,
                            detail=f"{session_data.session_type.capitalize()} session already logged today")

    # Auto-generate session_id if not provided
    if session_data.session_id is None:
        last_session = (
            db.query(DialysisSession)
            .filter(DialysisSession.patient_id == session_data.patient_id)
            .order_by(DialysisSession.session_id.desc())
            .first()
        )
        session_data.session_id = last_session.session_id + 1 if last_session else 1

    try:
        new_session = DialysisSession(
            patient_id=session_data.patient_id,
            session_type=session_data.session_type,
            session_id=session_data.session_id,
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

        logger.info(
            f"Dialysis session logged successfully for patient {session_data.patient_id} on {new_session.session_date}")

        # Notify clients about the new session
        await notify_clients({"message": "New dialysis session logged", "session": new_session})

        return new_session

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error logging dialysis session: {e}")
        raise HTTPException(status_code=400, detail="Integrity error: possible duplicate entry")
    except Exception as e:
        db.rollback()
        logger.error(f"Error logging dialysis session: {e}")
        raise HTTPException(status_code=500, detail="Failed to log dialysis session")


#  Route: `GET /dialysis/sessions`
@router.get("/sessions", response_model=List[DialysisSessionResponse])
async def get_dialysis_sessions(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        patient_id: Optional[int] = None,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    """
    Retrieve dialysis sessions for a patient within a given date range.
    Providers can specify a patient_id to fetch sessions for a specific patient.
    """
    try:
        # If the user is a patient, ensure they can only fetch their own sessions
        if user.role == "patient":
            if patient_id and patient_id != user.id:
                logger.warning(f"Patient {user.id} attempted to access another patient's sessions")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            patient_id = user.id

        # If the user is a provider, ensure a valid patient_id is provided
        elif user.role == "provider":
            if not patient_id:
                logger.warning(f"Provider {user.id} did not specify a patient_id")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Patient ID is required for providers")

        # Query dialysis sessions for the specified patient
        query = db.query(DialysisSession).filter(DialysisSession.patient_id == patient_id)
        if start_date:
            query = query.filter(DialysisSession.session_date >= start_date)
        if end_date:
            query = query.filter(DialysisSession.session_date <= end_date)
        sessions = query.all()

        logger.info(f"Retrieved {len(sessions)} dialysis sessions for patient {patient_id}")
        return sessions

    except Exception as e:
        logger.error(f"Error retrieving dialysis sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dialysis sessions")



@router.put("/sessions/{session_id}", response_model=DialysisSessionResponse)
async def update_dialysis_session(
        session_id: int,
        session_data: DialysisSessionCreate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    """Allows a patient to update their dialysis session if entered incorrectly."""

    # Find the existing session
    session = db.query(DialysisSession).filter(
        DialysisSession.id == session_id,
        DialysisSession.patient_id == user.id  # Ensures patient can only edit their own session
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Dialysis session not found")

    try:
        # Update fields
        session.session_type = session_data.session_type
        session.session_id = session_data.session_id
        session.weight = session_data.weight
        session.diastolic = session_data.diastolic
        session.systolic = session_data.systolic
        session.effluent_volume = session_data.effluent_volume
        session.session_date = session_data.session_date
        session.session_duration = session_data.session_duration
        session.protein = session_data.protein

        db.commit()
        db.refresh(session)

        logger.info(f"Dialysis session {session_id} updated successfully by patient {user.id}")
        return session

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating dialysis session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update dialysis session")


@router.get("/all-sessions", response_model=List[DialysisSessionResponse])
async def get_all_dialysis_sessions(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    """Allows a provider to view all patient dialysis sessions safely."""

    # ✅ Ensure user is a provider
    if user.role != "provider":
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        #  Fetch all sessions for all patients
        sessions = db.query(DialysisSession).all()
        logger.info(f"Provider {user.id} retrieved all patient dialysis sessions.")
        return sessions

    except Exception as e:
        logger.error(f"Error retrieving all dialysis sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dialysis sessions")


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_dialysis_session(
        session_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    """Allows a patient to delete their own dialysis session."""

    #  Find the session and check ownership
    session = db.query(DialysisSession).filter(
        DialysisSession.id == session_id,
        DialysisSession.patient_id == user.id  # Ensures patient can only delete their own session
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Dialysis session not found")

    try:
        db.delete(session)
        db.commit()
        logger.info(f"Dialysis session {session_id} deleted successfully by patient {user.id}")
        return {"message": "Dialysis session deleted successfully"}

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting dialysis session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete dialysis session")



