import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.db.session import get_db
from app.db.models.user import User
from app.db.models.dialysis import DialysisSession
from app.core.security import hash_password
import app.api.analytics as analytics
from app.db.fhir_integration import sync_fhir_create_patient_resource # (patient_id, name, birth_date, gender, height)
from datetime import datetime, timedelta
import random
import asyncio
import requests


def _create_provider(name_id, patients):
    return User(
        name=f"testuser{name_id} PROVIDER",
        email=f"testuser{name_id}@devnull.com",
        password=hash_password("password123"),
        role="provider",
        birth_date=f"1994-01-01",
        patients=patients,
        sex="male",
        height=175,
        notifications={
            "lowBloodPressure": False,
            "highBloodPressure": False,
            "dialysisGrowthAdjustment": False,
            "fluidOverloadHigh": False,
            "fluidOverloadWatch": False,
            "effluentVolume": False,
            "protein": False
        }
    )

def _create_patient(name_id, age, sex, height):
    return User(
        name=f"testuser{name_id} PATIENT",
        email=f"testuser{name_id}@devnull.com",
        password=hash_password("password123"),
        role="patient",
        birth_date=f"{2025 - age}-01-01",
        patients=[],
        sex=sex,
        height=height,
        notifications={
            "lowBloodPressure": False,
            "highBloodPressure": False,
            "dialysisGrowthAdjustment": False,
            "fluidOverloadHigh": False,
            "fluidOverloadWatch": False,
            "effluentVolume": False,
            "protein": False
        }
    )


def _gen_stable_patient_dialysis_sessions(patient_id, start_session_id, days, age, gender, height, start_weight):
    bp_ref = analytics.get_bp_reference_values(age, gender, height)
    high_systolic, high_diastolic = bp_ref["90th"]
    low_systolic, low_diastolic = bp_ref["50th"]

    # want to generate bp values s.t. (low_systolic, high_systolic) / (low_diastolic, high_diastolic) randomly
    sid = start_session_id
    pid = patient_id
    sessions = [
        DialysisSession(
            patient_id=pid, session_type="pre", session_id=sid,
            weight=start_weight, systolic=random.randint(low_systolic + 1, high_systolic - 1),
            diastolic=random.randint(low_diastolic + 1, high_diastolic - 1), effluent_volume=0.0,
            session_date="2025-04-16", session_duration=f"{0} hours",
            protein=12
        ),
        DialysisSession(
            patient_id=pid, session_type="post", session_id=sid + 1,
            weight=start_weight - random.uniform(0, 0.02)*start_weight, systolic=random.randint(low_systolic + 1, high_systolic - 1),
            diastolic=random.randint(low_diastolic + 1, high_diastolic - 1), effluent_volume=0.5 + random.uniform(0, 1),
            session_date="2025-04-16", session_duration=f"{round(random.uniform(1, 3), 1)} hours",
            protein=12
        ),]
    sid += 2

    sessions += [

        DialysisSession(
            patient_id=patient_id, session_type="pre", session_id=sid,
            weight=start_weight, systolic=random.randint(low_systolic + 1, high_systolic - 1),
            diastolic=random.randint(low_diastolic + 1, high_diastolic - 1), effluent_volume=0.0,
            session_date="2025-04-17", session_duration=f"{0} hours",
            protein=12
        ),
        DialysisSession(
            patient_id=patient_id, session_type="post", session_id=sid + 1,
            weight=start_weight - random.uniform(0, 0.02)*start_weight, systolic=random.randint(low_systolic + 1, high_systolic - 1),
            diastolic=random.randint(low_diastolic + 1, high_diastolic - 1), effluent_volume=0.5 + random.uniform(0, 1),
            session_date="2025-04-17", session_duration=f"{round(random.uniform(1, 3), 1)} hours",
            protein=12
        )]


    return sessions



def main():
    db = next(get_db())

    records = [
        (_create_patient(4, 17, "female", 175),
         _gen_stable_patient_dialysis_sessions(4, 3, 7, 17, "female", 175, 62)),
        (_create_provider(5, patients=[4]), [])
    ]

    users = [user for user,data in records]

    db.add_all(users)
    db.commit()

    for user in users:
        resp = sync_fhir_create_patient_resource(user.id, user.name, user.birth_date, user.sex, user.height)

    dialysis_sessions = [data for user,data in records]
    dialysis_sessions = [session for sessions in dialysis_sessions for session in sessions]

    db.add_all(dialysis_sessions)
    db.commit()

    db.close()

if __name__ == "__main__":
    main()