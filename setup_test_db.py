#!/usr/bin/env python3
"""
Script to set up the test database for PostgreSQL.
This script creates the test database and runs migrations.
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.config import settings
from app.database import Base

def create_test_database():
    """Create the test database if it doesn't exist"""
    # Connect to default PostgreSQL database
    default_url = "postgresql://postgres:postgres@localhost:5432/postgres"
    
    try:
        engine = create_engine(default_url)
        
        # Check if test database exists
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'practice_test'"))
            if not result.fetchone():
                # Create test database
                conn.execute(text("CREATE DATABASE practice_test"))
                print("✅ Test database 'practice_test' created successfully")
            else:
                print("✅ Test database 'practice_test' already exists")
                
    except Exception as e:
        print(f"❌ Error creating test database: {e}")
        print("Make sure PostgreSQL is running and accessible")
        return False
    
    return True

def setup_test_tables():
    """Create tables in the test database"""
    try:
        # Connect to test database
        test_engine = create_engine(settings.database_url_test)
        
        # Create all tables
        Base.metadata.create_all(bind=test_engine)
        print("✅ Test tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating test tables: {e}")
        return False
    
    return True

def main():
    print("Setting up test database...")
    
    # Create test database
    if not create_test_database():
        sys.exit(1)
    
    # Create tables
    if not setup_test_tables():
        sys.exit(1)
    
    print("🎉 Test database setup completed successfully!")
    print("You can now run the tests with: python run_tests.py")

if __name__ == "__main__":
    main()
