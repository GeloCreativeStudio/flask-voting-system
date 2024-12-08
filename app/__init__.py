from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Ensure the instance folder exists
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    try:
        os.makedirs(instance_path, exist_ok=True)
    except OSError:
        pass
        
    # Load config
    from app.config import Config
    app.config.from_object(Config)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Set up login configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        # Check if user_id is for admin (prefixed with 'a_')
        if user_id.startswith('a_'):
            from app.core.models import Admin
            return Admin.query.get(int(user_id[2:]))
        from app.core.models import Voter
        return Voter.query.get(int(user_id))

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.core.routes import core_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(core_bp)

    with app.app_context():
        db.create_all()
        from app.core.models import Admin
        Admin.create_default_admin()

    return app
