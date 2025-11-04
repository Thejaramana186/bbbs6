#!/usr/bin/env python3
"""
Script to create the PostgreSQL database on AWS RDS
Run this script to create the bbbs_db database on your PostgreSQL server
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the bbbs_db database on PostgreSQL server"""
    
    # Database connection parameters
    host = "bbbs-dev-db.cb0ck4cy4h1a.us-east-2.rds.amazonaws.com"
    port = 5432
    user = "postgres"
    password = "PjVZzlKywH>Nl3H10c-g5hs#<P)O"
    database_name = "bbbs_db"
    
    try:
        # Connect to PostgreSQL server (to postgres database)
        print("Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"  # Connect to default postgres database first
        )
        
        # Set autocommit mode
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database already exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (database_name,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"Database '{database_name}' already exists!")
        else:
            # Create the database
            print(f"Creating database '{database_name}'...")
            cursor.execute(f'CREATE DATABASE "{database_name}"')
            print(f"Database '{database_name}' created successfully!")
        
        cursor.close()
        conn.close()
        
        print("\nDatabase setup completed!")
        print("You can now update your .env file to use PostgreSQL:")
        print(f"DATABASE_URL=postgresql://{user}:{password}@{host}:{port}/{database_name}")
        
    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
        print("\nFalling back to SQLite for local development...")
        print("Your application will use SQLite database instead.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    create_database()