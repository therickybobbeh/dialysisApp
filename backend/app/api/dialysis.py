import logging
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Set ,Dict
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

    #  Check if patient exists
    patient = db.query(User).filter(User.id == session_data.patient_id, User.role == "patient").first()
    if not patient:
        logger.error(f"Patient with ID {session_data.patient_id} does not exist.")
        raise HTTPException(status_code=400, detail="Invalid patient ID: Patient does not exist")

    #  Check for duplicate session
    existing_session = (
        db.query(DialysisSession)
        .filter(
            DialysisSession.patient_id == session_data.patient_id,
            DialysisSession.session_date >= session_data.session_date.date()
        )
        .first()
    )
    if existing_session:
        logger.warning(f"Duplicate session detected for patient {session_data.patient_id} on {session_data.session_date}")
        raise HTTPException(status_code=400, detail="Dialysis session already logged today")

    try:
        new_session = DialysisSession(
            patient_id=session_data.patient_id,  #  Use the provided patient_id
            pre_weight=session_data.pre_weight,
            post_weight=session_data.post_weight,
            pre_systolic=session_data.pre_systolic,
            pre_diastolic=session_data.pre_diastolic,
            post_systolic=session_data.post_systolic,
            post_diastolic=session_data.post_diastolic,
            effluent_volume=session_data.effluent_volume,
            session_date=session_data.session_date,
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        logger.info(f"Dialysis session logged successfully for patient {session_data.patient_id} on {new_session.session_date}")

        return new_session

    except Exception as e:
        db.rollback()
        logger.error(f"Error logging dialysis session: {e}")
        raise HTTPException(status_code=500, detail="Failed to log dialysis session")






#  Route: `GET /dialysis/sessions`
@router.get("/sessions", response_model=List[DialysisSessionResponse])
async def get_dialysis_sessions(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieve dialysis sessions for a patient within a given date range."""
    if user.role != "patient":
        logger.warning(f"Unauthorized attempt to fetch dialysis sessions by user {user.id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        query = db.query(DialysisSession).filter(DialysisSession.patient_id == user.id)
        if start_date:
            query = query.filter(DialysisSession.session_date >= start_date)
        if end_date:
            query = query.filter(DialysisSession.session_date <= end_date)
        sessions = query.all()
        logger.info(f"Retrieved {len(sessions)} dialysis sessions for patient {user.id}")
        return sessions
    except Exception as e:
        logger.error(f"Error retrieving dialysis sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dialysis sessions")


#   Route: `GET /dialysis/provider-dashboard`
@router.get("/provider-dashboard")
async def provider_dashboard(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
) -> List[Dict]:
    """Fetches all PD patients and flags high-risk patients based on trends."""

    if user.role != "provider":
        logger.warning(f"Unauthorized access attempt to provider dashboard by user {user.id}")
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        #  Fetch all PD patients
        patients = db.query(User).filter(User.role == "patient").all()
        patient_ids = [p.id for p in patients]

        if not patient_ids:
            return []

        #  Apply date filters if provided
        last_30_days = datetime.utcnow() - timedelta(days=30)
        date_filter = last_30_days if not start_date else start_date
        end_date = end_date if end_date else datetime.utcnow()

        #  Fetch dialysis session data
        recent_sessions = (
            db.query(
                DialysisSession.patient_id,
                func.count(DialysisSession.id).label("session_count"),
                func.avg(DialysisSession.pre_weight).label("avg_pre_weight"),
                func.avg(DialysisSession.post_weight).label("avg_post_weight"),
                func.avg(DialysisSession.pre_systolic).label("avg_pre_systolic"),
                func.avg(DialysisSession.pre_diastolic).label("avg_pre_diastolic"),
                func.avg(DialysisSession.post_systolic).label("avg_post_systolic"),
                func.avg(DialysisSession.post_diastolic).label("avg_post_diastolic"),
                func.avg(DialysisSession.effluent_volume).label("avg_effluent"),
            )
            .filter(DialysisSession.patient_id.in_(patient_ids))
            .filter(DialysisSession.session_date >= date_filter)
            .filter(DialysisSession.session_date <= end_date)
            .group_by(DialysisSession.patient_id)
            .all()
        )

        #  Process and flag high-risk patients
        flagged_patients = []
        for row in recent_sessions:
            patient = next((p for p in patients if p.id == row.patient_id), None)
            if not patient:
                continue

            risk_level = "Low"
            high_risk_reasons = []

            # 🚨 **Risk Conditions**
            if row.session_count < 5:
                risk_level = "Medium"
                high_risk_reasons.append("Missed sessions in last 30 days")

            weight_change = abs(row.avg_post_weight - row.avg_pre_weight)
            if weight_change > 2.0:
                risk_level = "High"
                high_risk_reasons.append(f"Significant weight fluctuation: ±{weight_change:.1f} kg")

            if row.avg_pre_systolic > 140 or row.avg_post_systolic > 140:
                risk_level = "High"
                high_risk_reasons.append("Consistently high blood pressure detected")

            if row.avg_effluent < 1.5:
                risk_level = "High"
                high_risk_reasons.append("Low effluent volume detected")

            flagged_patients.append({
                "patient_id": row.patient_id,
                "patient_name": patient.name,
                "session_count": row.session_count,
                "avg_pre_weight": row.avg_pre_weight,
                "avg_post_weight": row.avg_post_weight,
                "avg_pre_systolic": row.avg_pre_systolic,
                "avg_post_systolic": row.avg_post_systolic,
                "avg_effluent": row.avg_effluent,
                "risk_level": risk_level,
                "issues": high_risk_reasons
            })

        #  Sort by risk level (High → Medium → Low)
        flagged_patients.sort(key=lambda x: ["Low", "Medium", "High"].index(x["risk_level"]), reverse=True)

        logger.info("Provider dashboard analytics generated successfully")
        return flagged_patients

    except Exception as e:
        logger.error(f"Error retrieving provider dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve provider dashboard analytics")


@router.put("/sessions/{session_id}", response_model=DialysisSessionResponse)
async def update_dialysis_session(
    session_id: int,
    session_data: DialysisSessionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Allows a patient to update their dialysis session if entered incorrectly."""

    #  Find the existing session
    session = db.query(DialysisSession).filter(
        DialysisSession.id == session_id,
        DialysisSession.patient_id == user.id  # Ensures patient can only edit their own session
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Dialysis session not found")

    try:
        #  Update fields
        session.pre_weight = session_data.pre_weight
        session.post_weight = session_data.post_weight
        session.pre_systolic = session_data.pre_systolic
        session.pre_diastolic = session_data.pre_diastolic
        session.post_systolic = session_data.post_systolic
        session.post_diastolic = session_data.post_diastolic
        session.effluent_volume = session_data.effluent_volume

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
    
@router.get("/patient/live-updates", tags=["Dialysis"])
async def get_live_dialysis_updates(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Fetch recent dialysis sessions for the logged-in patient.
    """

    #  Ensure only patients can access
    if user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied")

    #  Fetch DISTINCT sessions from the last 5 minutes
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    recent_sessions = (
        db.query(DialysisSession)
        .filter(DialysisSession.patient_id == user.id)
        .filter(DialysisSession.session_date >= five_minutes_ago)
        .order_by(DialysisSession.session_date.desc())
        .distinct(DialysisSession.session_date)  #  Ensure DISTINCT values
        .all()
    )

    #  Return empty list instead of raising an error
    return recent_sessions if recent_sessions else {"message": "No recent updates found."}


@router.get("/provider/live-updates", tags=["Dialysis"])
async def get_provider_live_updates(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """
    Fetch live dialysis session updates **for all patients (Provider View)**.
    """

    #  Ensure only providers can access
    if user.role != "provider":
        raise HTTPException(status_code=403, detail="Access denied")

    #  Fetch DISTINCT sessions from the last 5 minutes for **all patients**
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    recent_sessions = (
        db.query(DialysisSession)
        .filter(DialysisSession.session_date >= five_minutes_ago)
        .order_by(DialysisSession.session_date.desc())
        .distinct(DialysisSession.session_date)
        .all()
    )

    return recent_sessions if recent_sessions else {"message": "No recent updates found."}


