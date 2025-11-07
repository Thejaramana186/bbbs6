from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Connect to the default "postgres" database first
default_db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
engine = create_engine(default_db_url)

with engine.connect() as conn:
    conn.execute(text("COMMIT"))
    conn.execute(text("CREATE DATABASE bbbs_db"))
    print("✅ Database 'bbbs_db' created successfully.")
