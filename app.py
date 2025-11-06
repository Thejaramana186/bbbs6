from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os

# =====================================================
# Initialize Flask extensions
# =====================================================
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


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
    # Initialize extensions
    # -------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

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
    from controllers.notification_controller import notification_bp  # ✅ Added for notifications

    # Register all blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(loom_bp)
    app.register_blueprint(weaver_bp)
    app.register_blueprint(notification_bp)  # ✅ Register notification routes

    # -------------------------------------------------
    # Return the configured app
    # -------------------------------------------------
    return app
