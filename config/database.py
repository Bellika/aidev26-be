import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build database URL from Railway variables or use DATABASE_URL
# Railway provides: MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE
def get_database_url():
    # Try to get complete URL first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    # Otherwise, build from individual components (Railway style)
    mysql_user = os.getenv("MYSQL_USER", os.getenv("MYSQLUSER"))
    mysql_password = os.getenv("MYSQL_PASSWORD", os.getenv("MYSQLPASSWORD"))
    mysql_host = os.getenv("MYSQL_HOST", os.getenv("MYSQLHOST"))
    mysql_port = os.getenv("MYSQL_PORT", os.getenv("MYSQLPORT"))
    mysql_database = os.getenv("MYSQL_DATABASE", os.getenv("MYSQLDATABASE"))

    if all([mysql_user, mysql_host, mysql_port, mysql_database]):
        # Build URL from components
        password_part = f":{mysql_password}" if mysql_password else ""
        return f"mysql+pymysql://{mysql_user}{password_part}@{mysql_host}:{mysql_port}/{mysql_database}"

    # Fallback for local development
    return "mysql+pymysql://root:@localhost:3306/aidev_web"

DATABASE_URL = get_database_url()
print(f"Connecting to database: {DATABASE_URL.split('@')[0]}@***")  # Log without exposing full credentials

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
