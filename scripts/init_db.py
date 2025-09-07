import os
import sys

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.db.session import engine
from app.models.models import Base


def init_db():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    try:
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        return True
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False


if __name__ == "__main__":
    init_db()
