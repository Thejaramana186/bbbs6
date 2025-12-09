from app import create_app, db
import os
from dotenv import load_dotenv

# Import your models so SQLAlchemy knows about tables
from models.payments import Payment   # <-- add this
# If you have more models, import them too:
# from models.looms import Loom
# from models.materials import Material

# Load environment variables
load_dotenv()

app = create_app()

if __name__ == '__main__':
    # Create necessary directories
    directories = ['static/uploads', 'static/css', 'static/js', 'static/images']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Create all tables (INCLUDING payments)
    with app.app_context():
        db.create_all()   # <-- THIS creates payments table if missing

    # Run application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )