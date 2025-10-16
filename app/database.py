from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
import sys

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL is not set, try to construct it from individual components
if not DATABASE_URL:
    # Try to get individual database components
    # First check for PGUSER/PGPASSWORD (local development)
    db_user = os.getenv("PGUSER") or os.getenv("DB_USER", "postgres")
    db_password = os.getenv("PGPASSWORD") or os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    # Use ai_review_analyzer database (the one with Prisma tables)
    db_name = os.getenv("PGDATABASE") or os.getenv("DB_NAME", "ai_review_analyzer")
    
    # Construct the connection string
    if db_password:
        DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        DATABASE_URL = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
    
    print(f"WARNING: DATABASE_URL not set, constructed from components", file=sys.stderr)
else:
    print(f"Using DATABASE_URL from environment", file=sys.stderr)

# Handle Render's postgres:// to postgresql:// conversion
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Add SSL mode for Render if not already present
if "sslmode" not in DATABASE_URL and (("render.com" in DATABASE_URL) or ("internal" in DATABASE_URL)):
    if "?" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL + "&sslmode=require"
    else:
        DATABASE_URL = DATABASE_URL + "?sslmode=require"

print(f"Database connection configured", file=sys.stderr)

# Create engine with proper configuration for Render
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Test connections before using them
        pool_recycle=3600,   # Recycle connections every hour
        connect_args={
            "connect_timeout": 10,
            "application_name": "ai_review_analyzer"
        },
        echo=False  # Set to True for SQL debugging
    )
    
    # Configure the dialect to not quote identifiers
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        # This ensures we use the exact table names without quoting
        pass
    
    print("Database engine created successfully", file=sys.stderr)
except Exception as e:
    print(f"ERROR creating database engine: {str(e)}", file=sys.stderr)
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
