from app import create_app, db
app = create_app()

with app.app_context():
    conn = db.engine.connect()
    print("✅ Connected to DB:", conn.engine.url)
