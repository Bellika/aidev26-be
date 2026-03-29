import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection URL from environment variable
# Format: mysql+pymysql://username:password@host:port/database
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/aidev_web")

# Database settings from environment variables
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "True").lower() == "true"
DATABASE_POOL_PRE_PING = os.getenv("DATABASE_POOL_PRE_PING", "True").lower() == "true"
DATABASE_POOL_RECYCLE = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))

# Create the database engine
engine = create_engine(
    DATABASE_URL,
    echo=DATABASE_ECHO,  # Set to False in production to disable SQL logging
    pool_pre_ping=DATABASE_POOL_PRE_PING,  # Verify connections before using them
    pool_recycle=DATABASE_POOL_RECYCLE  # Recycle connections after 1 hour
)

# Create a SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for our models
Base = declarative_base()


def get_db():
    """
    Dependency function that provides a database session.
    Yields a database session and ensures it's closed after use.

    Usage in routes:
        @router.get("/")
        async def some_route(db: Session = Depends(get_db)):
            # Use db here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.
    This should be called when the application starts.
    """
    from models.user import User  # Import models here to avoid circular imports
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
