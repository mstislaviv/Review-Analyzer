from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
import sys

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL is not set, use fallback for local development
if not DATABASE_URL:
    DATABASE_URL = "postgresql://sandbox:kdof5H6A6ofkBCJL05dh9HWd@localhost:5432/ai_review_analyzer_fastapi"
    print(f"WARNING: DATABASE_URL not set, using fallback: {DATABASE_URL}", file=sys.stderr)
else:
    print(f"Using DATABASE_URL from environment", file=sys.stderr)

# Handle Render's postgres:// to postgresql:// conversion
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Add SSL mode for Render
if "sslmode" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL + "?sslmode=require"

print(f"Connecting to database: {DATABASE_URL.split('@')[0]}@{DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'unknown'}", file=sys.stderr)

# Create engine with proper configuration for Render
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Test connections before using them
        pool_recycle=3600,   # Recycle connections every hour
        connect_args={
            "connect_timeout": 10,
            "application_name": "ai_review_analyzer"
        }
    )
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
