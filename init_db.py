import os
import sys

# Set up environment before importing app modules
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')
os.environ.setdefault('DB_USER', 'postgres')
os.environ.setdefault('DB_NAME', 'ai_review_analyzer_fastapi')

from app.database import engine
from app.models import Base

print("=" * 50)
print("Initializing Database Tables")
print("=" * 50)

try:
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    print("=" * 50)
except Exception as e:
    print(f"❌ Error creating tables: {str(e)}")
    print("=" * 50)
    sys.exit(1)
