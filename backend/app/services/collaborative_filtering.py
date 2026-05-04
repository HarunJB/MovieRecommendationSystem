import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from app import db
from app.models.interaction import UserMovieInteraction
from app.models.movie import Movie


def get_collaborative_recommendations(user_id, n=10, exclude_movie_ids=None):
    if exclude_movie_ids is None:
        exclude_movie_ids = set()

    interactions = UserMovieInteraction.query.filter(
        UserMovieInteraction.rating != None
    ).all()

    if not interactions:
        return []

    user_ids = sorted(set(i.user_id for i in interactions))
    movie_ids = sorted(set(i.movie_id for i in interactions))

    user_index = {uid: idx for idx, uid in enumerate(user_ids)}
    movie_index = {mid: idx for idx, mid in enumerate(movie_ids)}
    index_movie = {idx: mid for mid, idx in movie_index.items()}

    if user_id not in user_index:
        return []

    rows = [user_index[i.user_id] for i in interactions]
    cols = [movie_index[i.movie_id] for i in interactions]
    data = [i.rating for i in interactions]

    matrix = csr_matrix(
        (data, (rows, cols)),
        shape=(len(user_ids), len(movie_ids))
    )

    matrix_dense = matrix.toarray().astype(float)
    user_ratings_mean = np.true_divide(
        matrix_dense.sum(1),
        (matrix_dense != 0).sum(1),
        where=(matrix_dense != 0).sum(1) != 0
    )
    matrix_demeaned = matrix_dense.copy()
    for i in range(matrix_dense.shape[0]):
        mask = matrix_dense[i] != 0
        matrix_demeaned[i][mask] -= user_ratings_mean[i]

    k = min(50, min(matrix_demeaned.shape) - 1)
    U, sigma, Vt = svds(csr_matrix(matrix_demeaned), k=k)
    sigma = np.diag(sigma)

    user_idx = user_index[user_id]
    predicted_ratings = np.dot(np.dot(U, sigma), Vt)[user_idx] + user_ratings_mean[user_idx]

    sorted_indices = np.argsort(predicted_ratings)[::-1]

    recommendations = []
    for idx in sorted_indices:
        mid = index_movie[idx]
        if mid not in exclude_movie_ids:
            recommendations.append((mid, float(predicted_ratings[idx])))
        if len(recommendations) >= n * 2:
            break

    return recommendations