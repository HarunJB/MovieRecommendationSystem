from app.services.collaborative_filtering import get_collaborative_recommendations
from app.services.content_based_filtering import get_content_based_recommendations
from app.models.movie import Movie
from app.models.interaction import UserMovieInteraction


def get_hybrid_recommendations(user_id, n=10, cf_weight=0.6, cb_weight=0.4):
    rated = UserMovieInteraction.query.filter_by(user_id=user_id).all()
    exclude_movie_ids = set(i.movie_id for i in rated)

    cf_recs = get_collaborative_recommendations(user_id, n=n * 2, exclude_movie_ids=exclude_movie_ids)
    cb_recs = get_content_based_recommendations(user_id, n=n * 2, exclude_movie_ids=exclude_movie_ids)

    def normalize(recs):
        if not recs:
            return {}
        scores = [score for _, score in recs]
        min_s, max_s = min(scores), max(scores)
        if max_s == min_s:
            return {mid: 1.0 for mid, _ in recs}
        return {mid: (score - min_s) / (max_s - min_s) for mid, score in recs}

    cf_scores = normalize(cf_recs)
    cb_scores = normalize(cb_recs)

    all_movie_ids = set(cf_scores.keys()) | set(cb_scores.keys())

    hybrid_scores = {}
    for mid in all_movie_ids:
        cf_score = cf_scores.get(mid, 0.0)
        cb_score = cb_scores.get(mid, 0.0)
        hybrid_scores[mid] = (cf_weight * cf_score) + (cb_weight * cb_score)

    sorted_movies = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)

    recommendations = []
    for mid, score in sorted_movies[:n]:
        movie = Movie.query.get(mid)
        if movie:
            movie_dict = movie.to_dict()
            movie_dict['hybrid_score'] = round(score, 4)
            recommendations.append(movie_dict)

    return recommendations