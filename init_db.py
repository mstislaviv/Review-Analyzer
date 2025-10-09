from app.database import engine
from app.models import Base
from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
