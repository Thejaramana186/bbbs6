from sqlalchemy import text
from app import create_app, db

app = create_app()

with app.app_context():
    result = db.session.execute(text("""
        SELECT conname
        FROM pg_constraint
        JOIN pg_class ON pg_constraint.conrelid = pg_class.oid
        WHERE pg_class.relname = 'looms';
    """))

    for row in result:
        print(row[0])
