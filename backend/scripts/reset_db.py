import sys
import os

# Adjust path to import FastAPI app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import Base, engine
from sqlalchemy.exc import SQLAlchemyError

def reset_database():
    """Drops all tables and recreates them."""
    try:
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped successfully.")

        print("Recreating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")

    except SQLAlchemyError as e:
        print(f"Database operation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()
