from app import db

movie_genre = db.Table(
    "movie_genre",
    db.Column(
        "movie_id", db.Integer, db.ForeignKey("movie.movie_id"), primary_key=True
    ),
    db.Column(
        "genre_id", db.Integer, db.ForeignKey("genre.genre_id"), primary_key=True
    ),
)


class Movie(db.Model):
    __tablename__ = "movie"

    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    release_year = db.Column(db.Integer)
    imdb_id = db.Column(db.Integer)
    tmdb_id = db.Column(db.Integer)
    avg_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    poster_path = db.Column(db.String(255), nullable=True)

    genres = db.relationship("Genre", secondary=movie_genre, backref="movies")
    interactions = db.relationship("UserMovieInteraction", backref="movie", lazy=True)

    def to_dict(self):
        return {
            "movie_id": self.movie_id,
            "title": self.title,
            "release_year": self.release_year,
            "imdb_id": self.imdb_id,
            "tmdb_id": self.tmdb_id,
            "avg_rating": self.avg_rating,
            "rating_count": self.rating_count,
            "genres": [g.name for g in self.genres],
        }

    def __repr__(self):
        return f"<Movie {self.title}>"


class Genre(db.Model):
    __tablename__ = "genre"

    genre_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Genre {self.name}>"


class Tag(db.Model):
    __tablename__ = "tag"

    tag_id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.movie_id"), nullable=False)
    tag = db.Column(db.String(255), nullable=False)
    count = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Tag {self.tag} on movie {self.movie_id}>"
