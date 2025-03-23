import sys
import os

# ✅ Ensure Backend Path is included
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Import models explicitly
from app.db.session import SessionLocal
from app.db.models.user import User  # Import User first
from app.db.models.food_intake import FoodIntake  # Import FoodIntake correctly
from app.core.security import hash_password
from sqlalchemy.orm import Session
from argon2 import PasswordHasher

db: Session = SessionLocal()
ph = PasswordHasher()

#  Fetch all users safely
'''users = db.query(User).all()
for user in users:
    if not user.password.startswith("$argon2"):  # Ensure only bcrypt passwords are rehashed
        print(f"Rehashing password for {user.email}")
        user.password = hash_password(user.password)  # Use their existing password
        db.add(user)'''


alice = db.query(User).filter(User.email == "drsmith@example.com").first()
if alice:
    alice.password = ph.hash("password123")  #  Rehash correctly
    db.commit()
    print(" Alice's password has been updated with Argon2!")
else:
    print(" Alice not found!")

db.commit()
print(" All user passwords updated to Argon2!")
