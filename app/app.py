from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

db = SQLAlchemy()
migrate = Migrate()
marshmallow = Marshmallow()
bcrypt = Bcrypt()


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)

    app.config.from_object("app.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    marshmallow.init_app(app)
    bcrypt.init_app(app)

    from app.api import docs_bp
    from app.routes import users_bp

    app.register_blueprint(users_bp, url_prefix="/api/v1/users")
    app.register_blueprint(docs_bp, url_prefix="/api/docs")

    return app
