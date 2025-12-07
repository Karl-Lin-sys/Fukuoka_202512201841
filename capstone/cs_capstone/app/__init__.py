from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_moment import Moment

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
bootstrap = Bootstrap5()
moment = Moment()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.jobs import bp as jobs_bp
    app.register_blueprint(jobs_bp, url_prefix='/jobs')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Error handlers
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User, 'Job': Job, 'Company': Company}

    return app

from app.models import User, Job, Company
