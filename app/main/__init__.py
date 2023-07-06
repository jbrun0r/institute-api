from logging.config import dictConfig

from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import config_by_name
from .logger import get_logging_config
from flask_cors import CORS 

db = SQLAlchemy()
migrate = Migrate()
app = Flask(__name__)
mail = Mail()
cors = CORS()


def create_app(config_name: str) -> Flask:
    app.config.from_object(config_by_name[config_name])
    dictConfig(get_logging_config())
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    cors.init_app(app)
    return app
