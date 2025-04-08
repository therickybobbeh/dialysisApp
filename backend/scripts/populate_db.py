import sys
import os
import logging
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from argon2 import PasswordHasher  # Use Argon2 for secure password hashing

# Ensure Backend Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, Base, engine
from app.db.models.user import User
from app.db.models.dialysis import DialysisSession

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure tables exist before inserting data
Base.metadata.create_all(bind=engine)
logger.info("Database tables verified.")

# Initialize Argon2 Hasher
ph = PasswordHasher()
db: Session = SessionLocal()

# Step 1: Create Test Users
users = [
    {"name": "Alice", "email": "alice@example.com", "password": "password123", "role": "patient"},
    {"name": "Bob", "email": "bob@example.com", "password": "password123", "role": "patient"},
    {"name": "Dr. Smith", "email": "drsmith@example.com", "password": "password123", "role": "provider"},
]

for user in users:
    existing_user = db.query(User).filter(User.email == user["email"]).first()
    if existing_user:
        logger.info(f"User {user['email']} already exists. Skipping.")
        continue

    hashed_password = ph.hash(user["password"])  # Hash password using Argon2
    db_user = User(name=user["name"], email=user["email"], password=hashed_password, role=user["role"])
    db.add(db_user)

try:
    db.commit()
    logger.info("Sample users added successfully!")
except IntegrityError:
    db.rollback()
    logger.error("Error: Duplicate user entry detected!")

# Step 2: Create Random Dialysis Sessions
patients = db.query(User).filter(User.role == "patient").all()
if not patients:
    logger.warning("No patient records found. Skipping dialysis session insertion.")

for patient in patients:
    for _ in range(5):
        session_type = random.choice(["pre", "post"])
        session_id = random.randint(1, 1000)
        weight = round(random.uniform(50, 80), 1)
        diastolic = random.randint(70, 90)
        systolic = random.randint(110, 130)
        effluent_volume = round(random.uniform(1.5, 3.0), 2)
        session_date = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))
        session_duration = f"{random.randint(1, 4)} hours"
        protein = round(random.uniform(0.1, 1.0), 2)

        session = DialysisSession(
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
        db.add(session)
db.commit()

try:
    db.commit()
    logger.info("Sample dialysis sessions added successfully!")
except IntegrityError:
    db.rollback()
    logger.error("Error: Duplicate dialysis session entry detected!")

db.close()
logger.info("Database session closed successfully.")