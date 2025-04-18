from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.session import get_db

# Example: Insert a single row
def insert_single_user(db: Session):
    user = User(
        id=1,
        name='Alice',
        email='alice@example.com',
        password='password123',
        role='admin',
        patients={},
        notifications={
            "lowBloodPressure": False,
            "highBloodPressure": True,
            "dialysisGrowthAdjustment": False,
            "fluidOverloadHigh": True,
            "fluidOverloadWatch": False,
            "effluentVolume": True,
            "protein": True
        },
        sex='female',
        height=165.5
    )
    db.add(user)
    db.commit()
    db.refresh(user)

# Example: Insert multiple rows
def insert_multiple_users(db: Session):
    users = [
        User(id=2, name='Bob', email='bob@example.com', password='password123', role='user', sex='male', height=180.2),
        User(id=3, name='Carol', email='carol@example.com', password='password123', role='user', sex='female', height=170.0),
    ]
    db.add_all(users)
    db.commit()

# Usage
if __name__ == "__main__":
    db = next(get_db())  # Assuming `get_db` is a generator function
    insert_single_user(db)
    insert_multiple_users(db)