import os
import sqlite3
from flask import Flask, g
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from .config import Config

load_dotenv()

login_manager = LoginManager()
mail = Mail()
scheduler = BackgroundScheduler()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(os.getenv('DATABASE_URL', 'medialert.db'))
        db.row_factory = sqlite3.Row
    return db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mail.init_app(app)
    login_manager.init_app(app)
    
    # Correct scheduler initialization
    scheduler.start()
    
    # Register scheduler shutdown when app context tears down
    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        if scheduler.running:
            scheduler.shutdown()

    login_manager.login_view = 'auth.login'

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
