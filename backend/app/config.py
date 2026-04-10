import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/movie_rec"
    )
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
