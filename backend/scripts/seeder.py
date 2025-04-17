import os
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.dialysis import DialysisSession
from app.db.models.food_intake import FoodIntake
from app.core.security import hash_password
from datetime import datetime, timedelta

def seed_data():
    db = next(get_db())

    # Ensure Users Are Seeded
    if db.query(User).count() == 0:
        print("🌱 Seeding users table...")
        users = [
            {
                "name": "Alice",
                "email": "alice@example.com",
                "password": "password123",
                "role": "patient",
                "patients": {},
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
                "password": "password456",
                "role": "patient",
                "patients": {},
                "notifications": {
                    "lowBloodPressure": True,
                    "highBloodPressure": False,
                    "dialysisGrowthAdjustment": True,
                    "fluidOverloadHigh": False,
                    "fluidOverloadWatch": True,
                    "effluentVolume": False,
                    "protein": True
                }
            },
            {
                "name": "Dr. Smith",
                "email": "drsmith@example.com",
                "password": "provider123",
                "role": "provider",
                "patients": {1, 2, 6},
                "notifications": {
                    "lowBloodPressure": True,
                    "highBloodPressure": True,
                    "dialysisGrowthAdjustment": False,
                    "fluidOverloadHigh": True,
                    "fluidOverloadWatch": True,
                    "effluentVolume": False,
                    "protein": False
                }
            },
        ]
        db.add_all(users)
        db.commit()
        print(" Users seeded successfully.")

    # Ensure Dialysis Sessions Are Seeded
    if db.query(DialysisSession).count() == 0:
        print("🌱 Seeding dialysis_sessions table...")
        dialysis_sessions = [
            DialysisSession(
                patient_id=1, session_type="pre", session_id=1, weight=65.2,
                diastolic=80, systolic=120, effluent_volume=2.0,
                session_date=datetime.utcnow() - timedelta(days=2), session_duration="3 hours",
                protein=12
            ),
            DialysisSession(
                patient_id=2, session_type="post", session_id=2, weight=78.1,
                diastolic=85, systolic=130, effluent_volume=1.8,
                session_date=datetime.utcnow() - timedelta(days=1), session_duration="3.5 hours",
                protein=15
            ),
        ]
        db.add_all(dialysis_sessions)
        db.commit()
        print(" Dialysis sessions seeded successfully.")

    # Ensure Food Intake Data Is Seeded
    if db.query(FoodIntake).count() == 0:
        print(" Seeding food_intake table...")
        food_intakes = [
            FoodIntake(patient_id=1, food_name="Grilled Chicken", protein_grams=35, meal_time=datetime.utcnow()),
            FoodIntake(patient_id=2, food_name="Scrambled Eggs", protein_grams=22, meal_time=datetime.utcnow()),
        ]
        db.add_all(food_intakes)
        db.commit()
        print(" Food intake records seeded successfully.")

    db.close()

if __name__ == "__main__":
    seed_data()