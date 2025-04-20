import logging
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Set
from datetime import datetime

from app.db.fhir_integration import (
    fhir_create_dialysis_session_resource,
    fhir_search_dialysis_sessions, fhir_delete_dialysis_session_resource,
)
from app.db.session import get_db
from app.db.models.dialysis import DialysisSession
from app.db.models.user import User
from app.db.schemas.dialysis import DialysisSessionCreate, DialysisSessionResponse
from app.core.security import get_current_user
from app.helpers.date_time import normalize_to_utc_day_bounds
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dialysis", tags=["Dialysis"])
active_connections: Set[WebSocket] = set()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    logger.info(f"New WebSocket connection established ({len(active_connections)} active clients)")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.warning(f"WebSocket client disconnected ({len(active_connections)} active clients)")

async def notify_clients(data: dict):
    disconnected = []
    for conn in active_connections:
        try:
            await conn.send_json(data)
        except Exception as e:
            logger.error(f"Error sending WebSocket update: {e}")
            disconnected.append(conn)
    for conn in disconnected:
        active_connections.remove(conn)

@router.post("/sessions", response_model=DialysisSessionResponse)
async def log_dialysis_session(
    session_data: DialysisSessionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Log or update a dialysis session and mirror it to FHIR."""
    patient = (
        db.query(User)
        .filter(User.id == session_data.patient_id, User.role == "patient")
        .first()
    )
    if not patient:
        logger.error(f"Patient {session_data.patient_id} does not exist")
        raise HTTPException(400, "Invalid patient ID")
    # Update existing by session_id
    if session_data.session_id is not None:
        existing = (
            db.query(DialysisSession)
            .filter(
                DialysisSession.session_id == session_data.session_id,
                DialysisSession.patient_id == session_data.patient_id,
            )
            .first()
        )
        if existing:
            for field in (
                "session_type","weight","diastolic","systolic",
                "effluent_volume","session_date","session_duration","protein",
            ):
                setattr(existing, field, getattr(session_data, field))
            try:
                db.commit(); db.refresh(existing)
                logger.info(f"DB: updated session {existing.session_id}")
            except Exception as db_err:
                db.rollback(); logger.error(f"DB error: {db_err}")
                raise HTTPException(500, "Failed to update session")

            logger.info(f"FHIR: about to update session with date {existing.session_date.date()}")
            try:
                duration = datetime.strptime(existing.session_duration, '%Y-%m-%dT%H:%M:%S.%fZ')
                hrs, mins = duration.hour, duration.minute
                hrs -= datetime.now().hour
                true_duration = hrs * 60 + mins
                await fhir_create_dialysis_session_resource(
                    session_id=existing.session_id,
                    patient_id=existing.patient_id,
                    date=existing.session_date.date(),
                    session_type=existing.session_type,
                    weight=existing.weight,
                    diastolic=existing.diastolic,
                    systolic=existing.systolic,
                    effluent_volume=existing.effluent_volume,
                    duration=true_duration,
                    protein=existing.protein,
                )
                logger.info(f"FHIR: updated session {existing.session_id}")
            except Exception as fhir_err:
                logger.error(f"FHIR error: {fhir_err}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Session updated locally but failed to update FHIR",
                )
            await notify_clients({"message": "Session updated", "session": existing})
            return existing
    # Duplicate same-day check
    dup = (
        db.query(DialysisSession)
        .filter(
            DialysisSession.patient_id == session_data.patient_id,
            DialysisSession.session_type == session_data.session_type,
            func.date(DialysisSession.session_date) == session_data.session_date.date(),
        )
        .first()
    )
    if dup:
        logger.warning("Duplicate session")
        raise HTTPException(400, f"{session_data.session_type.capitalize()} session already logged today")
    # Auto-generate session_id
    if session_data.session_id is None:
        last = (
            db.query(DialysisSession)
            .filter(DialysisSession.patient_id == session_data.patient_id)
            .order_by(DialysisSession.session_id.desc())
            .first()
        )
        session_data.session_id = (last.session_id + 1) if last else 1
    # Insert new
    try:
        new_sess = DialysisSession(**session_data.dict())
        db.add(new_sess); db.commit(); db.refresh(new_sess)
        logger.info(f"DB: created session {new_sess.session_id}")
    except IntegrityError as ie:
        db.rollback(); logger.error(f"Integrity error: {ie}")
        raise HTTPException(400, "Integrity error: possible duplicate")
    except Exception as db_err:
        db.rollback(); logger.error(f"DB error: {db_err}")
        raise HTTPException(500, "Failed to log dialysis session")
    # logger.info(f"FHIR: about to create session with date {new_sess.session_date.date().strftime('%Y-%m-%d'), type(new_sess.session_date.date().strftime('%Y-%m-%d'))}")
    # logger.info(f"{new_sess.session_id} {new_sess.patient_id} {new_sess.session_date.date()} {new_sess.session_type} "
    #             f"{new_sess.weight} {new_sess.diastolic} {new_sess.systolic} {new_sess.effluent_volume} "
    #             f"{datetime.strptime(new_sess.session_duration, '%Y-%m-%dT%H:%M:%S.%fZ').minute} "
    #             f"{new_sess.protein}")
    try:
        duration = datetime.strptime(new_sess.session_duration, '%Y-%m-%dT%H:%M:%S.%fZ')
        hrs, mins = duration.hour, duration.minute
        hrs -= datetime.now().hour
        true_duration = hrs * 60 + mins
        await fhir_create_dialysis_session_resource(
            session_id=new_sess.session_id,
            patient_id=new_sess.patient_id,
            date=new_sess.session_date.date(),
            session_type=new_sess.session_type,
            weight=new_sess.weight,
            diastolic=new_sess.diastolic,
            systolic=new_sess.systolic,
            effluent_volume=new_sess.effluent_volume,
            duration=true_duration,
            protein=new_sess.protein,
        )
        logger.info(f"FHIR: created session {new_sess.session_id}")
    except Exception as fhir_err:
        logger.error(f"FHIR error: {fhir_err}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Session saved locally but failed to create on FHIR",
        )
    await notify_clients({"message": "New session logged", "session": new_sess})
    return new_sess

@router.get(
    "/sessions",
    response_model=List[DialysisSessionResponse],
)
async def get_dialysis_sessions(
    start_date: Optional[datetime] = None,
    end_date:   Optional[datetime] = None,
    patient_id: Optional[int]      = None,
    db:         Session            = Depends(get_db),
    user:       User               = Depends(get_current_user),
):
    # auth & patient resolution
    if user.role == "patient":
        if patient_id and patient_id != user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")
        patient_id = user.id
    elif user.role == "provider":
        if not patient_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Patient ID is required")
    else:
        patient_id = patient_id or user.id
    # normalize dates
    start_dt, end_dt = normalize_to_utc_day_bounds(start_date, end_date)
    # FHIR search
    try:
        fhir_sessions = await fhir_search_dialysis_sessions(
            patient_id=patient_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=1000,
        )
    except Exception as fhir_err:
        logger.error(f"FHIR error: {fhir_err}")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Failed to fetch from FHIR server")
    return [DialysisSessionResponse(**s) for s in fhir_sessions]

@router.put(
    "/sessions/{session_id}",
    response_model=DialysisSessionResponse,
)
async def update_dialysis_session(
    session_id:    int,
    session_data:  DialysisSessionCreate,
    db:            Session = Depends(get_db),
    user:          User    = Depends(get_current_user),
):
    session = (
        db.query(DialysisSession)
        .filter(DialysisSession.id == session_id,
                DialysisSession.patient_id == user.id)
        .first()
    )
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    for field in (
        "session_type","session_id","weight","diastolic",
        "systolic","effluent_volume","session_date",
        "session_duration","protein",
    ):
        setattr(session, field, getattr(session_data, field))
    try:
        db.commit(); db.refresh(session)
    except Exception as db_err:
        db.rollback(); logger.error(f"DB error: {db_err}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to save session")
    try:
        duration = datetime.strptime(session.session_duration, '%Y-%m-%dT%H:%M:%S.%fZ')
        hrs, mins = duration.hour, duration.minute
        hrs -= datetime.now().hour
        true_duration = hrs * 60 + mins
        await fhir_create_dialysis_session_resource(
            session_id=session.session_id,
            patient_id=session.patient_id,
            date=session.session_date.date(),
            session_type=session.session_type,
            weight=session.weight,
            diastolic=session.diastolic,
            systolic=session.systolic,
            effluent_volume=session.effluent_volume,
            duration=true_duration,
            protein=session.protein,
        )
    except Exception as fhir_err:
        logger.error(f"FHIR error: {fhir_err}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Session saved locally but failed to update FHIR",
        )
    return DialysisSessionResponse.from_orm(session)


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_dialysis_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    patients_list = user.patients if isinstance(user.patients, list) else [user.patients]
    session = (
        db.query(DialysisSession)
        .filter(
            DialysisSession.session_id == session_id
        )
        .first()
    )
    if not session:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    # Delete from the FHIR server
    try:
        await fhir_delete_dialysis_session_resource(session_id=session.session_id)
        logger.info(f"FHIR: deleted session {session.session_id}")
    except Exception as fhir_err:
        logger.error(f"FHIR delete error: {fhir_err}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to delete session on FHIR server",
        )
    # Delete from the database
    try:
        db.delete(session)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Delete error: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to delete session from database")

    return