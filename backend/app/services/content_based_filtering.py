import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.movie import Movie, Tag
from app.models.interaction import UserMovieInteraction


def build_movie_profiles():
    movies = Movie.query.all()
    tags = Tag.query.all()

    tag_map = {}
    for t in tags:
        if t.movie_id not in tag_map:
            tag_map[t.movie_id] = []
        tag_map[t.movie_id].append(t.tag)

    movie_ids = []
    profiles = []

    for movie in movies:
        genre_str = ' '.join([g.name.lower().replace('-', ' ') for g in movie.genres])
        tag_str = ' '.join(tag_map.get(movie.movie_id, []))
        profile = f"{genre_str} {tag_str}".strip()
        movie_ids.append(movie.movie_id)
        profiles.append(profile if profile else 'unknown')

    return movie_ids, profiles


def get_content_based_recommendations(user_id, n=10, exclude_movie_ids=None):
    if exclude_movie_ids is None:
        exclude_movie_ids = set()

    liked_interactions = UserMovieInteraction.query.filter(
        UserMovieInteraction.user_id == user_id,
        UserMovieInteraction.rating >= 3.5
    ).all()

    if not liked_interactions:
        return []

    liked_movie_ids = set(i.movie_id for i in liked_interactions)

    movie_ids, profiles = build_movie_profiles()
    movie_index = {mid: idx for idx, mid in enumerate(movie_ids)}

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(profiles)

    liked_indices = [
        movie_index[mid] for mid in liked_movie_ids
        if mid in movie_index
    ]

    if not liked_indices:
        return []

    user_profile = np.asarray(tfidf_matrix[liked_indices].mean(axis=0))

    similarities = cosine_similarity(user_profile, tfidf_matrix).flatten()

    sorted_indices = np.argsort(similarities)[::-1]

    recommendations = []
    for idx in sorted_indices:
        mid = movie_ids[idx]
        if mid not in exclude_movie_ids and mid not in liked_movie_ids:
            recommendations.append((mid, float(similarities[idx])))
        if len(recommendations) >= n * 2:
            break

    return recommendations