import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

# =====================================================
# Initialize Flask extensions
# =====================================================
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()  # <-- Added for email/OTP support

# =====================================================
# Application Factory
# =====================================================
def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # -------------------------------------------------
    # Load configuration
    # -------------------------------------------------
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(Config)

    # -------------------------------------------------
    # Upload folder configuration
    # -------------------------------------------------
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    upload_folder = os.path.join(BASE_DIR, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    # -------------------------------------------------
    # Initialize extensions
    # -------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)  # <-- Attach mail to app

    # -------------------------------------------------
    # Flask-Login Configuration
    # -------------------------------------------------
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login user loader callback."""
        from models.user import User
        return User.query.get(int(user_id))

    # -------------------------------------------------
    # Register Blueprints
    # -------------------------------------------------
    from controllers.auth_controller import auth_bp
    from controllers.loom_controller import loom_bp
    from controllers.weaver_controller import weaver_bp
    from controllers.notification_controller import notification_bp
    from controllers.payments_controller import payments_bp

    app.register_blueprint(payments_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(loom_bp)
    app.register_blueprint(weaver_bp)
    app.register_blueprint(notification_bp)
    




    # -------------------------------------------------
    # Import Models for Flask-Migrate Auto-Detection
    # -------------------------------------------------
    from models.user import User
    from models.loom import Loom
    from models.weaver import Weaver
    # from models.notification import Notification

    return app

# =====================================================
# Flask CLI Integration (for `flask db` commands)
# =====================================================
app = create_app()

# =====================================================
# Main Entry Point
# =====================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
