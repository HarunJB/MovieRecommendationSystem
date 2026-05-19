from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from app import db
from app.models.movie import Movie
from app.models.interaction import UserMovieInteraction

movies_bp = Blueprint("movies", __name__)


@movies_bp.route('/movie/<int:movie_id>')
@login_required
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    user_interaction = UserMovieInteraction.query.filter_by(
        user_id=current_user.user_id,
        movie_id=movie_id
    ).first()
    source = request.args.get('from', 'dashboard')
    return render_template('movie.html', movie=movie, user_interaction=user_interaction, source=source)


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


@movies_bp.route("/api/movies/user-ratings")
@login_required
def get_user_ratings():
    page = request.args.get("page", 1, type=int)
    per_page = 10

    interactions = (
        UserMovieInteraction.query.filter_by(user_id=current_user.user_id)
        .order_by(UserMovieInteraction.rated_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    result = []
    for i in interactions.items:
        movie = Movie.query.get(i.movie_id)
        if movie:
            d = movie.to_dict()
            d["user_rating"] = i.rating
            d["rated_at"] = i.rated_at.isoformat()
            result.append(d)

    return jsonify(
        {
            "ratings": result,
            "total": interactions.total,
            "pages": interactions.pages,
            "current_page": page,
        }
    )


@movies_bp.route("/api/movies/user-stats")
@login_required
def get_user_stats():
    from sqlalchemy import func

    result = (
        db.session.query(
            func.count(UserMovieInteraction.rating).label("total"),
            func.avg(UserMovieInteraction.rating).label("avg"),
        )
        .filter_by(user_id=current_user.user_id)
        .first()
    )

    return jsonify(
        {
            "total_ratings": result.total or 0,
            "avg_rating": round(float(result.avg), 1) if result.avg else 0,
        }
    )
