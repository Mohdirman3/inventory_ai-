"""
Initialize all tables on the cloud database (Aiven / Railway)
"""
import os
import sys

# Ensure backend root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine, Base
import app.database.models  # Registers all 7 models with Base.metadata

def init_db():
    print("Connecting to cloud database:", engine.url)
    print("Creating all tables from models.py...")
    Base.metadata.create_all(bind=engine)
    print("All 7 tables created successfully in the cloud database!")

if __name__ == "__main__":
    init_db()
