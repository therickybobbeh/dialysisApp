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

    #  Ensure Users Are Seeded
    if db.query(User).count() == 0:
        print("🌱 Seeding users table...")
        users = [
            User(name="Alice", email="alice@example.com", password=hash_password("password123"), role="patient"),
            User(name="Bob", email="bob@example.com", password=hash_password("password456"), role="patient"),
            User(name="Dr. Smith", email="drsmith@example.com", password=hash_password("provider123"), role="provider"),
        ]
        db.add_all(users)
        db.commit()
        print(" Users seeded successfully.")

    #  Ensure Dialysis Sessions Are Seeded
    if db.query(DialysisSession).count() == 0:
        print("🌱 Seeding dialysis_sessions table...")
        dialysis_sessions = [
            DialysisSession(
                patient_id=1, pre_weight=65.2, post_weight=63.8,
                pre_systolic=120, pre_diastolic=80, post_systolic=115, post_diastolic=75,
                effluent_volume=2.0, session_date=datetime.utcnow() - timedelta(days=2)
            ),
            DialysisSession(
                patient_id=2, pre_weight=78.1, post_weight=76.5,
                pre_systolic=130, pre_diastolic=85, post_systolic=125, post_diastolic=80,
                effluent_volume=1.8, session_date=datetime.utcnow() - timedelta(days=1)
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
