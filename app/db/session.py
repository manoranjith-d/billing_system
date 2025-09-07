from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Enable connection pool "pre-ping" feature
    pool_size=5,  # Set the pool size
    max_overflow=10,  # Maximum number of connections to allow over the pool size
    pool_timeout=30,  # Timeout for getting a connection from the pool
)

# Create SessionLocal class with custom settings
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
