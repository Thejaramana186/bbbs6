from app import db, create_app

def init_db():
    """Initialize the database with all tables"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()