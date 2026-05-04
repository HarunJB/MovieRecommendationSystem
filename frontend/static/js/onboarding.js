let allMovies = [];
let ratedMovies = {}; // { movieId: rating }
let activeGenre = "all";

document.addEventListener("DOMContentLoaded", async () => {
  await loadMovies();
  document
    .getElementById("movie-search")
    .addEventListener("input", filterMovies);
});

async function loadMovies() {
  try {
    const data = await apiFetch("/api/movies/onboarding");
    allMovies = data;
    buildGenreFilters(data);
    renderMovies(data);
    document.getElementById("onboarding-footer").style.display = "block";
  } catch (err) {
    document.getElementById("movie-grid").innerHTML =
      `<div class="col-12 text-center text-danger py-4">Failed to load movies. Please refresh.</div>`;
  }
}

function buildGenreFilters(movies) {
  const genreSet = new Set();
  movies.forEach((m) => m.genres.forEach((g) => genreSet.add(g)));

  const container = document.getElementById("genre-filters");
  [...genreSet].sort().forEach((genre) => {
    const btn = document.createElement("button");
    btn.className = "btn btn-sm btn-outline-secondary genre-btn";
    btn.dataset.genre = genre;
    btn.textContent = genre;
    btn.onclick = () => setGenre(genre, btn);
    container.appendChild(btn);
  });
}

function setGenre(genre, btn) {
  activeGenre = genre;
  document
    .querySelectorAll(".genre-btn")
    .forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  filterMovies();
}

function filterMovies() {
  const query = document.getElementById("movie-search").value.toLowerCase();
  let filtered = allMovies;

  if (activeGenre !== "all") {
    filtered = filtered.filter((m) => m.genres.includes(activeGenre));
  }
  if (query) {
    filtered = filtered.filter((m) => m.title.toLowerCase().includes(query));
  }
  renderMovies(filtered);
}

function renderMovies(movies) {
  const grid = document.getElementById("movie-grid");
  if (movies.length === 0) {
    grid.innerHTML = `<div class="col-12 text-center text-muted py-4">No movies found.</div>`;
    return;
  }

  grid.innerHTML = movies
    .map((m) => {
      const rating = ratedMovies[m.movie_id] || 0;
      const selected = rating > 0 ? "selected" : "";
      const poster = m.poster_path
        ? `<img src="https://image.tmdb.org/t/p/w200${m.poster_path}" class="movie-poster-img" alt="${m.title}">`
        : `<div class="movie-poster"><i class="bi bi-film"></i></div>`;
      return `
    <div class="col-6 col-sm-4 col-md-3 col-lg-2">
        <div class="card movie-card ${selected}" id="card-${m.movie_id}">
            ${poster}
            <div class="card-body">
                <p class="movie-title mb-1">${m.title}</p>
                <small class="text-muted d-block mb-2">${m.release_year || ""}</small>
                ${renderStars(rating, m.movie_id, true)}
            </div>
        </div>
    </div>`;
    })
    .join("");
}

function updateProgress(movieId, rating) {
  if (rating === 0) {
    delete ratedMovies[movieId];
    const card = document.getElementById(`card-${movieId}`);
    if (card) card.classList.remove("selected");
  } else {
    ratedMovies[movieId] = rating;
    const card = document.getElementById(`card-${movieId}`);
    if (card) card.classList.add("selected");
  }

  const count = Object.keys(ratedMovies).length;
  const pct = Math.min((count / 20) * 100, 100);

  document.getElementById("progress-bar").style.width = pct + "%";
  document.getElementById("progress-text").textContent =
    `${Math.min(count, 20)} / 20 rated`;
  document.getElementById("footer-count").textContent = Math.min(count, 20);

  const finishBtn = document.getElementById("finish-btn");
  finishBtn.disabled = count < 20;
}

async function finishOnboarding() {
  const btn = document.getElementById("finish-btn");
  btn.disabled = true;
  btn.textContent = "Saving...";

  try {
    const ratings = Object.entries(ratedMovies).map(([movieId, rating]) => ({
      movie_id: parseInt(movieId),
      rating: rating,
      is_onboarding: true,
    }));

    for (const r of ratings) {
      await rateMovie(r.movie_id, r.rating, true);
    }

    window.location.href = "/dashboard";
  } catch (err) {
    btn.disabled = false;
    btn.textContent = "Get My Recommendations →";
    alert("Something went wrong. Please try again.");
  }
}
