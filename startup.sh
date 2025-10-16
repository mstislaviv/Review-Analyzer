#!/bin/bash
set -e

echo "Starting AI Review Analyzer..."
echo "================================"

# Initialize database tables
echo "Initializing database tables..."
python3 init_db.py

# Start the FastAPI server
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
