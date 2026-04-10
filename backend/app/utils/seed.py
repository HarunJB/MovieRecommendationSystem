import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import re
from app import create_app, db
from app.models.movie import Movie, Genre, Tag
from app.models.interaction import UserMovieInteraction
from app.models.user import User

app = create_app()

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../../data")


def seed_movies():
    print("Seeding movies and genres...")
    genre_cache = {}

    with open(os.path.join(DATA_DIR, "movies.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            match = re.search(r"\((\d{4})\)$", row["title"].strip())
            year = int(match.group(1)) if match else None
            title = re.sub(r"\s*\(\d{4}\)$", "", row["title"].strip())

            movie = Movie(movie_id=int(row["movieId"]), title=title, release_year=year)
            db.session.add(movie)

            if row["genres"] != "(no genres listed)":
                for genre_name in row["genres"].split("|"):
                    if genre_name not in genre_cache:
                        genre = Genre.query.filter_by(name=genre_name).first()
                        if not genre:
                            genre = Genre(name=genre_name)
                            db.session.add(genre)
                            db.session.flush()
                        genre_cache[genre_name] = genre
                    movie.genres.append(genre_cache[genre_name])

    db.session.commit()
    print(f"Done. Genres seeded: {len(genre_cache)}")


def seed_links():
    print("Seeding links (imdb/tmdb)...")
    with open(os.path.join(DATA_DIR, "links.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie = Movie.query.get(int(row["movieId"]))
            if movie:
                movie.imdb_id = int(row["imdbId"]) if row["imdbId"] else None
                movie.tmdb_id = int(float(row["tmdbId"])) if row["tmdbId"] else None
    db.session.commit()
    print("Done.")


def seed_ratings():
    print("Seeding synthetic users and ratings (this may take a while)...")
    user_cache = {}
    count = 0

    with open(os.path.join(DATA_DIR, "ratings.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = int(row["userId"])

            if user_id not in user_cache:
                user = User(
                    user_id=user_id,
                    username=f"synthetic_user_{user_id}",
                    email=f"synthetic_{user_id}@movielens.org",
                    onboarding_complete=True,
                )
                user.set_password("synthetic")
                db.session.add(user)
                db.session.flush()
                user_cache[user_id] = True

            interaction = UserMovieInteraction(
                user_id=user_id,
                movie_id=int(row["movieId"]),
                rating=float(row["rating"]),
                interaction_type="rated",
                is_onboarding=False,
            )
            db.session.add(interaction)
            count += 1

            if count % 5000 == 0:
                db.session.commit()
                print(f"  {count} ratings inserted...")

    db.session.commit()
    print(f"Done. {count} ratings seeded.")


def update_avg_ratings():
    print("Updating average ratings on movies...")
    from sqlalchemy import func

    results = (
        db.session.query(
            UserMovieInteraction.movie_id,
            func.avg(UserMovieInteraction.rating).label("avg"),
            func.count(UserMovieInteraction.rating).label("cnt"),
        )
        .group_by(UserMovieInteraction.movie_id)
        .all()
    )

    for r in results:
        movie = Movie.query.get(r.movie_id)
        if movie:
            movie.avg_rating = round(float(r.avg), 2)
            movie.rating_count = r.cnt

    db.session.commit()
    print("Done.")


def seed_tags():
    print("Seeding tags...")
    from collections import Counter

    tag_counts = Counter()

    with open(os.path.join(DATA_DIR, "tags.csv"), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie_id = int(row["movieId"])
            tag = row["tag"].strip().lower()
            tag_counts[(movie_id, tag)] += 1

    count = 0
    for (movie_id, tag), cnt in tag_counts.items():
        movie = Movie.query.get(movie_id)
        if movie:
            t = Tag(movie_id=movie_id, tag=tag, count=cnt)
            db.session.add(t)
            count += 1

    db.session.commit()
    print(f"Done. {count} tags seeded.")


def fetch_posters():
    import requests

    api_key = app.config["TMDB_API_KEY"]
    movies_list = Movie.query.filter(Movie.tmdb_id != None).all()
    print(f"Fetching posters for {len(movies_list)} movies...")
    count = 0

    for movie in movies_list:
        try:
            res = requests.get(
                f"https://api.themoviedb.org/3/movie/{movie.tmdb_id}",
                params={"api_key": api_key},
                timeout=5,
            )
            if res.status_code == 200:
                data = res.json()
                movie.poster_path = data.get("poster_path")
                count += 1
        except Exception:
            pass

        if count % 500 == 0 and count > 0:
            db.session.commit()
            print(f"  {count} posters fetched...")

    db.session.commit()
    print(f"Done. {count} posters fetched.")


if __name__ == "__main__":
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        fetch_posters()
        print("All done! Database is ready.")
