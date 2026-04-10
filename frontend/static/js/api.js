
async function apiFetch(url, options = {}) {
    const defaults = {
        headers: { 'Content-Type': 'application/json' }
    };
    const config = { ...defaults, ...options };
    const res = await fetch(url, config);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ error: 'Request failed' }));
        throw new Error(err.error || 'Request failed');
    }
    return res.json();
}

async function rateMovie(movieId, rating, isOnboarding = false) {
    return apiFetch('/api/movies/rate', {
        method: 'POST',
        body: JSON.stringify({ movie_id: movieId, rating, is_onboarding: isOnboarding })
    });
}

function renderStars(rating, movieId, isOnboarding = false) {
    const stars = [1, 2, 3, 4, 5];
    return `
        <div class="star-rating" id="stars-${movieId}">
            ${stars.map(i => `
                <i class="bi bi-star-fill star ${i <= rating ? 'rated' : ''}"
                   data-value="${i}"
                   data-movie="${movieId}"
                   data-onboarding="${isOnboarding}"
                   onclick="handleStarClick(this)">
                </i>`).join('')}
        </div>`;
}

function handleStarClick(el) {
    const movieId = parseInt(el.dataset.movie);
    const value = parseInt(el.dataset.value);
    const isOnboarding = el.dataset.onboarding === 'true';

    const container = document.getElementById(`stars-${movieId}`);
    const currentRating = parseInt(container.dataset.currentRating || 0);
    const newRating = currentRating === value ? 0 : value;

    container.dataset.currentRating = newRating;
    container.querySelectorAll('.star').forEach(s => {
        s.classList.toggle('rated', parseInt(s.dataset.value) <= newRating);
    });

    if (!isOnboarding) {
        rateMovie(movieId, newRating, false)
            .catch(err => console.error('Rating failed:', err));
    } else {
        if (typeof updateProgress === 'function') {
            updateProgress(movieId, newRating);
        }
    }
}
