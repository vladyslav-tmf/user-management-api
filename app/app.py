from flask import Flask
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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

    from app.routes import users_bp

    app.register_blueprint(users_bp, url_prefix="/api/v1")

    return app
