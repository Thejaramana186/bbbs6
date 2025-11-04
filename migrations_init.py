from flask import Flask
from flask_migrate import init, migrate, upgrade
from app import create_app, db
import os

def initialize_migrations():
    """Initialize Flask-Migrate for the project"""
    app = create_app()
    
    with app.app_context():
        try:
            # Initialize migration repository if it doesn't exist
            if not os.path.exists('migrations'):
                print("Initializing migration repository...")
                os.system('flask db init')
            
            # Create initial migration
            print("Creating initial migration...")
            os.system('flask db migrate -m "Initial migration"')
            
            # Apply migration to database
            print("Applying migration to database...")
            os.system('flask db upgrade')
            
            print("Database migrations completed successfully!")
            
        except Exception as e:
            print(f"Migration failed: {str(e)}")
            print("Creating tables directly...")
            db.create_all()
            print("Tables created successfully!")

if __name__ == '__main__':
    initialize_migrations()