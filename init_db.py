#!/usr/bin/env python3
"""
Database initialization script for AI Review Analyzer
Creates all necessary tables in PostgreSQL
"""

import os
from sqlalchemy import create_engine
from app.models import Base, User, Order, Payment
from app.database import DATABASE_URL

def init_db():
    """Initialize database tables"""
    try:
        print("🔄 Connecting to database...")
        engine = create_engine(DATABASE_URL)
        
        print("📊 Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        print("\nTables created:")
        print("  ✓ users")
        print("  ✓ orders")
        print("  ✓ payments")
        
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_db()
    exit(0 if success else 1)
