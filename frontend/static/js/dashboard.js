document.addEventListener('DOMContentLoaded', async () => {
    await loadRecommendations();
});

async function loadRecommendations() {
    try {
        const data = await apiFetch('/api/recommendations');
        const movies = data.recommendations;

        if (!movies || movies.length === 0) {
            document.getElementById('recommendations-grid').style.display = 'none';
            document.getElementById('empty-state').style.display = 'block !important';
            return;
        }

        renderRecommendations(movies);
    } catch (err) {
        document.getElementById('recommendations-grid').innerHTML =
            `<div class="col-12 text-center text-danger py-4">Failed to load recommendations.</div>`;
    }
}

function renderRecommendations(movies) {
    const grid = document.getElementById('recommendations-grid');
    grid.innerHTML = movies.map(m => `
        <div class="col-sm-6 col-md-4 col-lg-3">
            <div class="card movie-card h-100" onclick="window.location='/movie/${m.movie_id}'">
                <div class="movie-poster">
                    <i class="bi bi-film"></i>
                </div>
                <div class="card-body d-flex flex-column">
                    <h6 class="movie-title mb-1">${m.title}</h6>
                    <small class="text-muted mb-2">${m.release_year || ''}</small>
                    <div class="mt-auto">
                        <div class="d-flex flex-wrap gap-1 mb-2">
                            ${m.genres.slice(0, 2).map(g =>
                                `<span class="badge bg-secondary">${g}</span>`).join('')}
                        </div>
                        <span class="text-warning">
                            <i class="bi bi-star-fill"></i>
                            <small>${m.avg_rating ? m.avg_rating.toFixed(1) : 'N/A'}</small>
                        </span>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

async function searchMovies() {
    const query = document.getElementById('profile-search').value.trim();
    if (!query) return;

    const data = await apiFetch(`/api/movies/search?q=${encodeURIComponent(query)}`);
    const container = document.getElementById('search-results');

    if (!data.length) {
        container.innerHTML = `<p class="text-muted small">No movies found.</p>`;
        return;
    }

    container.innerHTML = data.map(m => `
        <div class="col-12">
            <div class="d-flex align-items-center justify-content-between py-2 border-bottom border-secondary">
                <div>
                    <span class="fw-bold">${m.title}</span>
                    <small class="text-muted ms-2">${m.release_year || ''}</small>
                </div>
                ${renderStars(0, m.movie_id, false)}
            </div>
        </div>
    `).join('');
}
