from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    app = Flask(
        __name__,
        template_folder="../../frontend/templates",
        static_folder="../../frontend/static",
    )

    app.config.from_object("app.config.Config")

    from app.models.user import User
    from app.models.movie import Movie, Genre
    from app.models.interaction import UserMovieInteraction

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    from app.routes.auth import auth
    from app.routes.movies import movies_bp
    from app.routes.recommendations import recommendations

    app.register_blueprint(auth)
    app.register_blueprint(movies_bp)
    app.register_blueprint(recommendations)

    return app
