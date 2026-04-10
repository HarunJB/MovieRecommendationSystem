from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from app import db
from app.models.movie import Movie
from app.models.interaction import UserMovieInteraction

movies_bp = Blueprint("movies", __name__)


@movies_bp.route("/movie/<int:movie_id>")
@login_required
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    user_interaction = UserMovieInteraction.query.filter_by(
        user_id=current_user.user_id, movie_id=movie_id
    ).first()
    return render_template("movie.html", movie=movie, user_interaction=user_interaction)


@movies_bp.route("/api/movies/onboarding")
@login_required
def get_onboarding_movies():
    """Returns 20 diverse movies for onboarding, spread across genres."""
    # TODO: implement smart selection logic (one per genre + top rated)
    movies_list = Movie.query.order_by(Movie.rating_count.desc()).limit(100).all()
    return jsonify([m.to_dict() for m in movies_list])


@movies_bp.route("/api/movies/search")
@login_required
def search_movies():
    query = request.args.get("q", "")
    movies_list = Movie.query.filter(Movie.title.ilike(f"%{query}%")).limit(20).all()
    return jsonify([m.to_dict() for m in movies_list])


@movies_bp.route("/api/movies/rate", methods=["POST"])
@login_required
def rate_movie():
    data = request.get_json()
    movie_id = data.get("movie_id")
    rating = data.get("rating")
    is_onboarding = data.get("is_onboarding", False)

    existing = UserMovieInteraction.query.filter_by(
        user_id=current_user.user_id, movie_id=movie_id
    ).first()

    if existing:
        existing.rating = rating
    else:
        interaction = UserMovieInteraction(
            user_id=current_user.user_id,
            movie_id=movie_id,
            rating=rating,
            interaction_type="rated",
            is_onboarding=is_onboarding,
        )
        db.session.add(interaction)

    if is_onboarding:
        count = UserMovieInteraction.query.filter_by(
            user_id=current_user.user_id, is_onboarding=True
        ).count()
        if count >= 20:
            current_user.onboarding_complete = True

    db.session.commit()
    return jsonify({"success": True})
