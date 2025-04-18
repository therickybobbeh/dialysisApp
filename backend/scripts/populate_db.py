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

# ---------------------------
# Step 1: Create Test Users
# ---------------------------
users = [
    {"name": "Alice", "email": "alice@example.com", "password": "password123", "role": "patient", "patients": {},
     "sex": "female", "height": 165.5,
     "notifications": {
         "lowBloodPressure": False,
         "highBloodPressure": True,
         "dialysisGrowthAdjustment": False,
         "fluidOverloadHigh": True,
         "fluidOverloadWatch": False,
         "effluentVolume": True,
         "protein": True
     }},
    {"name": "Bob", "email": "bob@example.com", "password": "password123", "role": "patient", "patients": {},
     "sex": "male", "height": 180.2,
     "notifications": {
         "lowBloodPressure": True,
         "highBloodPressure": False,
         "dialysisGrowthAdjustment": True,
         "fluidOverloadHigh": False,
         "fluidOverloadWatch": True,
         "effluentVolume": False,
         "protein": True
     }},
    # For a provider, assume `patients` is a set of patient IDs.
    {"name": "Dr. Smith", "email": "drsmith@example.com", "password": "password123", "role": "provider",
     "patients": {1, 2, 6}, "sex": "male", "height": 175.0,
     "notifications": {
         "lowBloodPressure": True,
         "highBloodPressure": True,
         "dialysisGrowthAdjustment": False,
         "fluidOverloadHigh": True,
         "fluidOverloadWatch": True,
         "effluentVolume": False,
         "protein": False
     }},
]

for user in users:
    existing_user = db.query(User).filter(User.email == user["email"]).first()
    if existing_user:
        logger.info(f"User {user['email']} already exists. Skipping.")
        continue

    hashed_password = ph.hash(user["password"])
    db_user = User(
        name=user["name"],
        email=user["email"],
        password=hashed_password,
        role=user["role"],
        sex=user["sex"],
        height=user["height"]
    )
    db.add(db_user)

try:
    db.commit()
    logger.info("Sample users added successfully!")

    # Reset the sequence for users_id_seq
    db.execute(
        text("SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1) + 1, false);")
    )
    db.commit()
    logger.info("Users sequence reset successfully.")
except IntegrityError as e:
    db.rollback()
    logger.error("Error inserting sample users:")
    logger.error(e)
except Exception as e:
    db.rollback()
    logger.error("Failed to reset users_id_seq sequence:")
    logger.error(e)

# ---------------------------------------
# Step 2: Create Random Dialysis Sessions
# ---------------------------------------
patients = db.query(User).filter(User.role == "patient").all()
if not patients:
    logger.warning("No patient records found. Skipping dialysis session insertion.")
else:
    for patient in patients:
        inserted_sessions_count = 0
        attempts = 0  # avoid infinite loops if duplicates keep occurring.
        while inserted_sessions_count < 5 and attempts < 10:
            attempts += 1
            session_type = random.choice(["pre", "post"])
            session_id = random.randint(1, 1000)
            weight = round(random.uniform(50, 80), 1)
            diastolic = random.randint(70, 90)
            systolic = random.randint(110, 130)
            effluent_volume = round(random.uniform(1.5, 3.0), 2)
            # Pick a random date within the past 30 days.
            session_date = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
            session_duration = f"{random.randint(1, 4)} hours"
            protein = round(random.uniform(0.1, 1.0), 2)

            # Check for an existing session on the same day and with the same session type.
            # We use func.date() to compare only the date part.
            existing = db.query(DialysisSession).filter(
                DialysisSession.patient_id == patient.id,
                DialysisSession.session_type == session_type,
                func.date(DialysisSession.session_date) == session_date.date()
            ).first()

            if existing:
                logger.info(
                    f"Session for patient {patient.id} on {session_date.date()} ({session_type}) already exists. Skipping this attempt.")
                continue

            new_session = DialysisSession(
                patient_id=patient.id,
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
    except IntegrityError as e:
        db.rollback()
        logger.error("Error inserting dialysis sessions:")
        logger.error(e)

    # Optional: Reset the sequence so that the next generated id is higher than the current max.
    try:
        db.execute(
            text("SELECT setval('dialysis_sessions_id_seq', COALESCE((SELECT MAX(id) FROM dialysis_sessions), 0))"))
        db.commit()
        logger.info("Dialysis sessions sequence reset successfully.")
    except Exception as e:
        db.rollback()
        logger.error("Failed to reset dialysis_sessions_id_seq sequence:")
        logger.error(e)

db.close()
logger.info("Database session closed successfully.")
