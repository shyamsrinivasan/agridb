from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
import os
from . import config


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
flask_bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # application configuration
    # app.config.from_object('config.DevConfig')
    app.config.from_object(config.DevConfig)
    app.config.from_pyfile('config.py')

    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Please log in for further access'
    login_manager.login_message_category = 'error'

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .admin import admin_bp
    from .user import user_bp
    from .data import data_bp
    from .visual import visual_bp
    from.analytics import analytic_bp

    # register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(data_bp, url_prefix='/data')
    app.register_blueprint(visual_bp, url_prefix='/visualize')
    app.register_blueprint(analytic_bp, url_prefix='/analyze')

    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db)
        db.create_all()

    return app


