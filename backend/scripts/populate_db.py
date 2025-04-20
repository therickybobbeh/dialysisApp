#!/usr/bin/env python3
import sys
import os
import logging
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, text
from argon2 import PasswordHasher

# Ensure backend path is added so we can import modules.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, Base, engine
from app.db.models.user import User
from app.db.models.dialysis import DialysisSession

# Configure logging.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create tables if they don’t exist.
Base.metadata.create_all(bind=engine)
logger.info("Database tables verified.")

ph = PasswordHasher()
db: Session = SessionLocal()

# Sample users to seed
users = [
    {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "password123",
        "role": "patient",
        "sex": "female",
        "height": 165.5,
        "birthdate": "1990-01-01",
        "notifications": {
            "lowBloodPressure": False,
            "highBloodPressure": True,
            "dialysisGrowthAdjustment": False,
            "fluidOverloadHigh": True,
            "fluidOverloadWatch": False,
            "effluentVolume": True,
            "protein": True
        }
    },
    {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "password123",
        "role": "patient",
        "sex": "male",
        "height": 180.2,
        "birthdate": "1985-05-15",
        "notifications": {
            "lowBloodPressure": True,
            "highBloodPressure": False,
            "dialysisGrowthAdjustment": True,
            "fluidOverloadHigh": False,
            "fluidOverloadWatch": True,
            "effluentVolume": False,
            "protein": True
        }
    }
]

# Seed users
for user in users:
    existing_user = db.query(User).filter(User.email == user["email"]).first()
    if existing_user:
        logger.info(f"User {user['email']} already exists. Skipping.")
        continue

    hashed_password = ph.hash(user["password"])
    # Generate a random birth date for ages between 2 and 17 years
    random_birth_date = datetime.now(timezone.utc) - timedelta(
        days=random.randint(2 * 365, 17 * 365)
    )
    db_user = User(
        name=user["name"],
        email=user["email"],
        password=hashed_password,
        role=user["role"],
        sex=user["sex"],
        height=user["height"],
        birth_date=user.get("birthdate", random_birth_date),
        notifications=user.get("notifications", {}),
        patients=list(user.get("patients", []))
    )
    db.add(db_user)

try:
    db.commit()
    logger.info("Sample users added successfully!")
    # Reset users sequence to next max+1
    db.execute(
        text(
            "SELECT setval('public.users_id_seq', COALESCE((SELECT MAX(id) FROM public.users), 1) + 1, true);"
        )
    )
    db.commit()
    logger.info("Users sequence reset successfully.")
except IntegrityError as e:
    db.rollback()
    logger.error(e)
except Exception as e:
    db.rollback()
    logger.error(e)

# Only seed dialysis sessions if none exist yet
if db.query(DialysisSession).count() == 0:
    # Determine starting session_id to avoid duplicates
    starting_session_id = db.query(func.max(DialysisSession.session_id)).scalar() or 0
    session_id_counter = starting_session_id

    # Seed dialysis sessions for each patient in our users list
    seeded_patient_ids = [db.query(User).filter(User.email == u["email"]).first().id for u in users]
    for patient_id in seeded_patient_ids:
        inserted_sessions_count = 0
        attempts = 0
        while inserted_sessions_count < 5 and attempts < 10:
            attempts += 1
            session_type = random.choice(["pre", "post"])
            # Use incremental session_id to guarantee uniqueness
            session_id_counter += 1
            session_id = session_id_counter

            weight = round(random.uniform(50, 80), 1)
            diastolic = random.randint(70, 90)
            systolic = random.randint(110, 130)
            effluent_volume = round(random.uniform(1.5, 3.0), 2)
            session_date = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
            session_duration = f"{random.randint(1, 4)} hours"
            protein = round(random.uniform(0.1, 1.0), 2)

            existing = db.query(DialysisSession).filter(
                DialysisSession.patient_id == patient_id,
                DialysisSession.session_type == session_type,
                func.date(DialysisSession.session_date) == session_date.date()
            ).first()

            if existing:
                continue

            new_session = DialysisSession(
                patient_id=patient_id,
                session_type=session_type,
                session_id=session_id,
                weight=weight,
                diastolic=diastolic,
                systolic=systolic,
                effluent_volume=effluent_volume,
                session_date=session_date,
                session_duration=session_duration,
                protein=protein
            )
            db.add(new_session)
            inserted_sessions_count += 1

    try:
        db.commit()
        logger.info("Sample dialysis sessions added successfully!")
        # Reset dialysis_sessions sequence to next max(id)+1
        db.execute(
            text(
                "SELECT setval('public.dialysis_sessions_id_seq', COALESCE((SELECT MAX(id) FROM public.dialysis_sessions), 1) + 1, true);"
            )
        )
        db.commit()
        logger.info("Dialysis sessions sequence reset successfully.")
    except IntegrityError as e:
        db.rollback()
        logger.error(e)
    except Exception as e:
        db.rollback()
        logger.error(e)
else:
    logger.info("Dialysis sessions already exist; skipping session seeding.")

# Close DB session
db.close()
logger.info("Database session closed successfully.")