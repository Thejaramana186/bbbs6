#!/usr/bin/env python3
"""
Initialize PostgreSQL database with all tables
"""

import os
from sqlalchemy import text, inspect
from app import create_app, db


def init_postgres_db():
    """Initialize PostgreSQL database with all tables"""

    # Ensure DATABASE_URL is set (can also be set in your .env file)
    os.environ['DATABASE_URL'] = (
        "postgresql://postgres:PjVZzlKywH>Nl3H10c-g5hs#<P)O@"
        "bbbs-dev-db.cb0ck4cy4h1a.us-east-2.rds.amazonaws.com:5432/bbbs_db"
    )

    app = create_app()

    with app.app_context():
        try:
            print("Connecting to PostgreSQL database...")

            # Test connection (SQLAlchemy 2.0 style)
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            print("Database connection successful!")

            # Drop all tables for a clean start
            print("Dropping existing tables...")
            db.drop_all()

            # Recreate all tables
            print("Creating all tables...")
            db.create_all()

            print("Database initialized successfully!")
            print("Database URL:", app.config["SQLALCHEMY_DATABASE_URI"])

            # Print created table names
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if tables:
                print(f"Created tables: {', '.join(tables)}")
            else:
                print("No tables were created. Check your models.")

        except Exception as e:
            print(f"Database initialization failed: {e}")
            print("Please make sure:")
            print("1. PostgreSQL server is running")
            print("2. Database 'bbbs_db' exists")
            print("3. Connection credentials are correct")
            raise


if __name__ == "__main__":
    init_postgres_db()
