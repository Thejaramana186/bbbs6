from db import db
from app import create_app
from sqlalchemy import text   # <-- import text

# create the Flask app
app = create_app()

with app.app_context():
    result = db.session.execute(
        text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'looms';")
    )
    for row in result:
        print(row)
