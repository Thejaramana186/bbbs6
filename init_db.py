from flask import Flask
from flask_migrate import init, migrate, upgrade
from app import create_app, db
import os

def initialize_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Try to create all tables
            db.create_all()
            print("Database tables created successfully!")
            
            # Print database info
            database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
            if 'postgresql' in database_url:
                print("Using PostgreSQL database")
            else:
                print("Using SQLite database")
                
        except Exception as e:
            print(f"Database initialization failed: {str(e)}")
            print("Please check your database connection settings.")

if __name__ == '__main__':
    initialize_database()