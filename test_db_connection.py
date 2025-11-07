import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Fetch environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Construct the PostgreSQL connection URL
DATABASE_URL = f"postgresql+psycopg2://postgres:zA#$9hCGw>))8GEj22|?pZsW!?r5@balajibros-devdb.cha00kc6y9nd.eu-north-1.rds.amazonaws.com:5432/bbbs_db"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Test connection
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW()"))
        for row in result:
            print("✅ Database connected successfully!")
            print("🕒 Current time:", row[0])
except Exception as e:
    print("❌ Database connection failed!")
    print("Error:", e)
