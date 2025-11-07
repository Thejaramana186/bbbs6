# test_db_connection.py
from db import engine

with engine.connect() as conn:
    result = conn.execute("SELECT NOW()")
    print(result.fetchone())
